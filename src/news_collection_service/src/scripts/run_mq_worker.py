"""RabbitMQ Worker script for collecting and publishing parsed news items."""

import asyncio
import json
from logging import getLogger

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from market_intel_lib.utils.file_storage import FileStorageFolder, FileStorageService
from market_intel_lib.utils.logger.configure import configure_logging
from market_intel_lib.utils.toml.ingest_toml import load_settings

from src.constants import MQ_WORKER_SETTINGS_PATH
from src.parsers.article_parser import ArticleParser
from src.services.data_collector import DataCollectorService
from src.settings import settings
from src.settings.models.mq_worker_settings_model import MQWorkerSettings

logger = getLogger(__name__)


async def main() -> None:
    """Main entry point for the RabbitMQ worker process."""
    logger.info("Starting RabbitMQ worker for News Collection Service")
    configure_logging(settings.service.logging_level)
    mq_worker_settings = load_settings(MQ_WORKER_SETTINGS_PATH, MQWorkerSettings)
    logger.info("MQ worker settings loaded from configuration file")

    connection = await connect_robust(
        host=mq_worker_settings.connector.host,
        port=mq_worker_settings.connector.port,
        virtualhost=mq_worker_settings.connector.virtual_host,
        heartbeat=mq_worker_settings.connector.heartbeat,
    )

    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            name=mq_worker_settings.exchange.name,
            type=ExchangeType(mq_worker_settings.exchange.type.value),
            durable=mq_worker_settings.exchange.durable,
            auto_delete=mq_worker_settings.exchange.auto_delete,
        )

        for queue_config in mq_worker_settings.send_queues:
            queue = await channel.declare_queue(
                name=queue_config.name,
                durable=queue_config.durable,
                auto_delete=queue_config.auto_delete,
                exclusive=queue_config.exclusive,
            )
            await queue.bind(exchange=exchange, routing_key=queue_config.routing_key)

        logger.info("Connected to RabbitMQ and queues are set up. Starting collection...")

        file_storage_service = FileStorageService()
        await file_storage_service.ensure_bucket()

        collector = DataCollectorService()
        article_parser = ArticleParser()

        async for item in collector.monitor():
            safe_pub_date = item.pub_date.replace("/", "-")

            raw_news_remote_object_name = file_storage_service.create_remote_object_name(
                FileStorageFolder.RAW_NEWS,
                f"{item.metadata.region}-{item.metadata.name}-{safe_pub_date}-{item.title}.html",
            )
            await file_storage_service.upload_text(
                item.raw_content or "",
                raw_news_remote_object_name,
                metadata={
                    "source": f"{item.metadata.region}/{item.metadata.name}",
                    "publication_date": safe_pub_date,
                    "title": item.title,
                },
            )

            item = article_parser.parse(item)

            extracted_news_remote_object_name = file_storage_service.create_remote_object_name(
                FileStorageFolder.EXTRACTED_NEWS,
                f"{item.metadata.region}-{item.metadata.name}-{safe_pub_date}-{item.title}.txt",
            )
            await file_storage_service.upload_text(
                item.prepared_content or "",
                extracted_news_remote_object_name,
                metadata={
                    "source": f"{item.metadata.region}/{item.metadata.name}",
                    "publication_date": safe_pub_date,
                    "title": item.title,
                },
            )

            if item.prepared_content is not None:
                item.raw_content = None

            try:
                body = json.dumps(item.model_dump(), ensure_ascii=False).encode()

                for queue_config in mq_worker_settings.send_queues:
                    await exchange.publish(
                        Message(
                            body=body,
                            delivery_mode=DeliveryMode(queue_config.delivery_mode),
                        ),
                        routing_key=queue_config.routing_key,
                    )

                logger.info(f"Published: [{item.metadata.region}/{item.metadata.name}] {item.title}")

            except Exception as e:
                logger.error(f"Failed to publish item '{item.title}': {e}")


def run() -> None:
    """Run the RabbitMQ worker."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
