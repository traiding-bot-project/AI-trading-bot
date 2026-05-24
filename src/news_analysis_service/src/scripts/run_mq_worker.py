"""RabbitMQ Worker script for processing content analysis tasks."""

import asyncio
import json
from logging import getLogger
from pathlib import Path

from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage

from src.constants import ANALYZE_NEWS_PROMPT, MQ_WORKER_SETTINGS_PATH
from src.interfaces import content_analyzer
from src.models.news_items import NewsItem
from src.models.ollama_api import OllamaCompletionRequest, OllamaCompletionResponse
from src.models.qwen_api import ChatMessage, QwenCompletionRequest, QwenCompletionResponse
from src.prompts.builder import load_and_format_prompt
from src.settings import settings
from src.settings.models.mq_worker_settings_model import MQWorkerSettings
from src.utils.ingest_toml import load_settings
from src.utils.logger import configure_logging

logger = getLogger(__name__)


async def main() -> None:
    """Main entry point for the RabbitMQ worker process."""
    logger.info("Starting RabbitMQ worker for News Analysis Service")
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

        for queue_config in mq_worker_settings.receive_queues + mq_worker_settings.send_queues:
            queue = await channel.declare_queue(
                name=queue_config.name,
                durable=queue_config.durable,
                auto_delete=queue_config.auto_delete,
                exclusive=queue_config.exclusive,
            )
            await queue.bind(exchange=exchange, routing_key=queue_config.routing_key)

        for receive_queue_config in mq_worker_settings.receive_queues:
            await channel.set_qos(prefetch_count=receive_queue_config.prefetch_count)

        logger.info("MQ worker connected to RabbitMQ and queues are set up. Waiting for messages...")

        async def on_message(message: AbstractIncomingMessage) -> None:
            """Process incoming message, analyze content, and publish results."""
            logger.info(f"New task received from input queue of the exchange {mq_worker_settings.exchange.name}")

            async with message.process(requeue=False):
                try:
                    data = NewsItem.model_validate(json.loads(message.body))
                    prompt = load_and_format_prompt(
                        Path(ANALYZE_NEWS_PROMPT),
                        news_item=data,
                        metadata=data.metadata,
                        description=data.description or "N/A",
                        prepared_content=data.prepared_content or "N/A",
                    )
                    logger.info("Prompt built for content analysis task")

                    active_deployment_key = settings.ai_model.active_deployment
                    if active_deployment_key == "ollama_deployments":
                        ollama_model = settings.ai_model.deployments.ollama_deployments.ollama_models[0]
                        ollama_request = OllamaCompletionRequest(model=ollama_model, prompt=prompt)
                        result = await content_analyzer.analyze_content(ollama_request)
                        if not isinstance(result, OllamaCompletionResponse):
                            raise TypeError("Expected OllamaCompletionResponse")
                        data.response = result.response
                        data.metadata.model_used = ollama_model.value
                    elif active_deployment_key == "qwen_deployments":
                        qwen_model = settings.ai_model.deployments.qwen_deployments.qwen_models[0]
                        qwen_request = QwenCompletionRequest(
                            model=qwen_model, messages=[ChatMessage(role="user", content=prompt)]
                        )
                        result = await content_analyzer.analyze_content(qwen_request)
                        if not isinstance(result, QwenCompletionResponse):
                            raise TypeError("Expected QwenCompletionResponse")
                        data.response = result.choices[0].message.content
                        data.metadata.model_used = qwen_model.value
                    else:
                        raise ValueError(f"Unsupported active deployment: {active_deployment_key}")

                    for send_queue_config in mq_worker_settings.send_queues:
                        await exchange.publish(
                            Message(
                                body=data.response.encode(),
                                delivery_mode=DeliveryMode(send_queue_config.delivery_mode),
                            ),
                            routing_key=send_queue_config.routing_key,
                        )

                    logger.info(
                        f"Task completed and sent to output queues of the exchange {mq_worker_settings.exchange.name}."
                    )

                except Exception as e:
                    logger.error(f"Processing failed: {e}")
                    raise

        for receive_queue_config in mq_worker_settings.receive_queues:
            queue = await channel.get_queue(receive_queue_config.name)
            await queue.consume(on_message)

        logger.info("Worker is listening. Press CTRL+C to exit.")
        try:
            await asyncio.get_event_loop().create_future()
        except asyncio.CancelledError:
            logger.info("Worker cancelled. Closing connection...")


def run() -> None:
    """Sync entry point for use as a pyproject.toml entrypoint."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
