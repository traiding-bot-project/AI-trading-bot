"""Test script to send a broadcast message to the Telegram user app service via RabbitMQ."""

import json

from pika import BlockingConnection, ConnectionParameters


def main() -> None:
    """Send a test broadcast message to the notification tasks queue."""
    # Connection parameters (same as in mq_worker_settings.toml)
    connection_params = ConnectionParameters(
        host="127.0.0.1",
        port=5672,
        virtual_host="/",
        heartbeat=600,
        socket_timeout=60000,
    )

    connection = BlockingConnection(connection_params)
    channel = connection.channel()

    # Declare exchange (same as worker)
    channel.exchange_declare(
        exchange="notification",
        exchange_type="direct",
        durable=True,
        auto_delete=False,
    )

    # Declare the tasks queue (in case it's not already declared)
    channel.queue_declare(
        queue="notification_tasks",
        durable=True,
        auto_delete=False,
        exclusive=False,
    )
    channel.queue_bind(
        queue="notification_tasks",
        exchange="notification",
        routing_key="tasks",
    )

    # Sample broadcast message
    broadcast_message = {
        "message": "📢 Breaking News: Important market update! Check your portfolio now.",
    }

    # Publish the message
    channel.basic_publish(
        exchange="notification",
        routing_key="tasks",
        body=json.dumps(broadcast_message),
    )

    print("Test broadcast message sent to notification_tasks queue.")

    connection.close()


if __name__ == "__main__":
    main()
