"""RabbitMQ Worker script for processing content analysis tasks."""

import asyncio
import json
from logging import getLogger

from pika import BlockingConnection, ConnectionParameters
from pika.channel import Channel
from pika.spec import Basic, BasicProperties

from src.constants import MQ_WORKER_SETTINGS_PATH
from src.interfaces import content_analyzer
from src.models.action_union_types import AnalyzeContentRequest
from src.settings import settings
from src.settings.models.mq_worker_settings_model import MQWorkerSettings
from src.utils.ingest_toml import load_settings
from src.utils.logger import configure_logging

logger = getLogger(__name__)


def main() -> None:
    """Main entry point for the RabbitMQ worker process."""
    logger.info("Starting RabbitMQ worker for News Analysis Service")
    configure_logging(settings.service.logging_level)
    mq_worker_settings = load_settings(MQ_WORKER_SETTINGS_PATH, MQWorkerSettings)
    logger.info("MQ worker settings loaded from configuration file")

    connection_params = ConnectionParameters(
        host=mq_worker_settings.connector.host,
        port=mq_worker_settings.connector.port,
        virtual_host=mq_worker_settings.connector.virtual_host,
        heartbeat=mq_worker_settings.connector.heartbeat,
        socket_timeout=mq_worker_settings.connector.socket_timeout,
    )

    connection = BlockingConnection(connection_params)
    channel = connection.channel()

    if any(send_queue.confirm for send_queue in mq_worker_settings.send_queues):
        channel.confirm_delivery()

    channel.exchange_declare(
        exchange=mq_worker_settings.exchange.name,
        exchange_type=mq_worker_settings.exchange.type.value,
        durable=mq_worker_settings.exchange.durable,
        auto_delete=mq_worker_settings.exchange.auto_delete,
    )

    for queue in mq_worker_settings.receive_queues + mq_worker_settings.send_queues:
        channel.queue_declare(
            queue=queue.name,
            durable=queue.durable,
            auto_delete=queue.auto_delete,
            exclusive=queue.exclusive,
        )
        channel.queue_bind(
            queue=queue.name,
            exchange=mq_worker_settings.exchange.name,
            routing_key=queue.routing_key,
        )

    for receive_queue in mq_worker_settings.receive_queues:
        channel.basic_qos(prefetch_count=receive_queue.prefetch_count)

    logger.info("MQ worker connected to RabbitMQ and queues are set up. Waiting for messages...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def on_message(ch: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
        """Process incoming message from RabbitMQ queue, analyze content, and publish results."""
        logger.info(f"New task received from input queue of the exchange {mq_worker_settings.exchange.name}")

        try:
            data = json.loads(body)
            request = AnalyzeContentRequest(**data)

            result = loop.run_until_complete(content_analyzer.analyze_content(request))

            for send_queue in mq_worker_settings.send_queues:
                ch.basic_publish(
                    exchange=mq_worker_settings.exchange.name,
                    routing_key=send_queue.routing_key,
                    body=json.dumps(result.model_dump()),
                    properties=BasicProperties(delivery_mode=send_queue.delivery_mode),
                )

            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(
                f"Task completed and sent to output queues of the exchange {mq_worker_settings.exchange.name}."
            )

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    for receive_queue in mq_worker_settings.receive_queues:
        channel.basic_consume(queue=receive_queue.name, on_message_callback=on_message)

    logger.info("Worker is listening. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Worker interrupted. Closing connection...")
        channel.stop_consuming()
        connection.close()
        loop.close()


if __name__ == "__main__":
    main()
