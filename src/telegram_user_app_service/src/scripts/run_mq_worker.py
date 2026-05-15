"""MQ Worker script to consume broadcast messages from RabbitMQ and send them via Telegram bot."""

import asyncio
from collections.abc import Callable, Coroutine
from logging import getLogger
from typing import Any

from aio_pika import ExchangeType, connect_robust
from aio_pika.abc import AbstractIncomingMessage
from src.constants import MQ_WORKER_SETTINGS_PATH
from src.models.bot import BroadcastRequest
from src.settings import settings
from src.settings.models.mq_worker_settings_model import (
    MQWorkerReceiveQueue,
    MQWorkerSettings,
)
from src.telegram.bot import broadcast_bot_context
from src.utils.ingest_toml import load_settings
from src.utils.logger import configure_logging

logger = getLogger(__name__)


def create_message_handler(
    queue_config: MQWorkerReceiveQueue,
) -> Callable[[AbstractIncomingMessage], Coroutine[Any, Any, None]]:
    """Create a message handler for a specific queue."""

    async def on_message(message: AbstractIncomingMessage) -> None:
        """Handle incoming broadcast messages."""
        logger.info(f"New broadcast message received from queue {queue_config.name}")

        try:
            text_data = message.body.decode("utf-8")
            logger.debug(f"Message data received as string: {text_data}")
            request = BroadcastRequest(response=text_data)

            await _broadcast_message(request)

            if queue_config.ack:
                await message.ack()
                logger.info(f"Message acknowledged for queue {queue_config.name}")

        except Exception as e:
            logger.error(f"Processing or broadcasting failed: {e}")
            await message.nack(requeue=False)

    return on_message


async def main() -> None:
    """Main function to run the RabbitMQ worker."""
    configure_logging(settings.service.logging_level)
    mq_worker_settings = load_settings(MQ_WORKER_SETTINGS_PATH, MQWorkerSettings)
    logger.info("Created MQ worker settings from configuration file")

    connection = await connect_robust(
        host=mq_worker_settings.connector.host,
        port=mq_worker_settings.connector.port,
        virtualhost=mq_worker_settings.connector.virtual_host,
        heartbeat=mq_worker_settings.connector.heartbeat,
    )

    async with connection:
        channel = await connection.channel()

        await channel.declare_exchange(
            name=mq_worker_settings.exchange.name,
            type=ExchangeType(mq_worker_settings.exchange.type.value),
            durable=mq_worker_settings.exchange.durable,
            auto_delete=mq_worker_settings.exchange.auto_delete,
        )

        for queue_config in mq_worker_settings.receive_queues:
            await channel.set_qos(prefetch_count=queue_config.prefetch_count)

            queue = await channel.declare_queue(
                name=queue_config.name,
                durable=queue_config.durable,
                auto_delete=queue_config.auto_delete,
                exclusive=queue_config.exclusive,
            )
            await queue.bind(
                exchange=mq_worker_settings.exchange.name,
                routing_key=queue_config.routing_key,
            )
            await queue.consume(create_message_handler(queue_config))

        logger.info("MQ worker connected to RabbitMQ and queues are set up. Waiting for messages...")
        logger.info("Worker is listening. Press CTRL+C to exit.")

        try:
            await asyncio.get_event_loop().create_future()
        except asyncio.CancelledError:
            logger.info("Worker cancelled. Closing connection...")


async def _broadcast_message(request: BroadcastRequest) -> None:
    """Broadcast a message to all subscribed Telegram users."""
    async with broadcast_bot_context() as bot:
        await bot.broadcast(request.message)
        logger.debug(f"Message broadcasted successfully: {request.message}")


def run() -> None:
    """Sync entry point for use as a pyproject.toml entrypoint."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
