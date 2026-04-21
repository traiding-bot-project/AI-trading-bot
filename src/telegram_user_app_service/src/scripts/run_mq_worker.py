"""MQ Worker script to consume broadcast messages from RabbitMQ and send them via Telegram bot."""

import asyncio
import json
from collections.abc import Callable
from logging import getLogger

from pika import BlockingConnection, ConnectionParameters
from pika.channel import Channel
from pika.spec import Basic, BasicProperties
from src.constants import MQ_WORKER_SETTINGS_PATH
from src.models.bot import BroadcastRequest
from src.settings import settings
from src.settings.models.mq_worker_settings_model import MQWorkerReceiveQueue, MQWorkerSettings
from src.telegram.bot import broadcast_bot_context
from src.utils.ingest_toml import load_settings
from src.utils.logger import configure_logging

logger = getLogger(__name__)

_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)


def create_message_handler(
    queue_settings: MQWorkerReceiveQueue,
) -> Callable[[Channel, Basic.Deliver, BasicProperties, bytes], None]:
    """Create a message handler for a specific queue."""

    def on_message(ch: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
        """Handle incoming broadcast messages."""
        logger.info(f"New broadcast message received from queue {queue_settings.name}")

        try:
            data = json.loads(body)
            request = BroadcastRequest(**data)

            _loop.run_until_complete(_broadcast_message(request))

            if queue_settings.ack:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Message acknowledged for queue {queue_settings.name}")

        except Exception as e:
            logger.error(f"Processing or broadcasting failed: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return on_message


def main() -> None:
    """Main function to run the RabbitMQ worker."""
    configure_logging(settings.service.logging_level)
    mq_worker_settings = load_settings(MQ_WORKER_SETTINGS_PATH, MQWorkerSettings)
    logger.info("Created MQ worker settings from configuration file")

    connection_params = ConnectionParameters(
        host=mq_worker_settings.connector.host,
        port=mq_worker_settings.connector.port,
        virtual_host=mq_worker_settings.connector.virtual_host,
        heartbeat=mq_worker_settings.connector.heartbeat,
        socket_timeout=mq_worker_settings.connector.socket_timeout,
    )

    connection = BlockingConnection(connection_params)
    channel = connection.channel()

    channel.exchange_declare(
        exchange=mq_worker_settings.exchange.name,
        exchange_type=mq_worker_settings.exchange.type.value,
        durable=mq_worker_settings.exchange.durable,
        auto_delete=mq_worker_settings.exchange.auto_delete,
    )

    for queue in mq_worker_settings.receive_queues:
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
        channel.basic_qos(prefetch_count=queue.prefetch_count)

    logger.info("MQ worker connected to RabbitMQ and queues are set up. Waiting for messages...")

    for receive_queue in mq_worker_settings.receive_queues:
        channel.basic_consume(queue=receive_queue.name, on_message_callback=create_message_handler(receive_queue))

    logger.info("Worker is listening. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Worker interrupted. Closing connection...")
        channel.stop_consuming()
        connection.close()
        _loop.close()


async def _broadcast_message(request: BroadcastRequest) -> None:
    """Broadcast a message to all subscribed Telegram users."""
    async with broadcast_bot_context() as bot:
        await bot.broadcast(request.message)
        logger.debug(f"Message broadcasted successfully: {request.message}")


if __name__ == "__main__":
    main()
