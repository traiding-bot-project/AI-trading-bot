"""Test script to receive messages from the news analysis microservice via RabbitMQ."""

import json

from pika import BlockingConnection, ConnectionParameters
from pika.channel import Channel
from pika.spec import Basic, BasicProperties


def main() -> None:
    """Receive test messages from the news analysis results queue."""
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
        exchange="news_analysis",
        exchange_type="direct",
        durable=True,
        auto_delete=False,
    )

    # Declare the results queue (in case it's not already declared)
    channel.queue_declare(
        queue="news_analysis_results",
        durable=True,
        auto_delete=False,
        exclusive=False,
    )
    channel.queue_bind(
        queue="news_analysis_results",
        exchange="news_analysis",
        routing_key="results",
    )

    def on_message(ch: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
        """Callback function to handle incoming messages."""
        try:
            data = json.loads(body)
            print("Received message:")
            print(json.dumps(data, indent=2))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    # Start consuming
    channel.basic_consume(queue="news_analysis_results", on_message_callback=on_message)

    print("Waiting for messages from news_analysis_results queue. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping consumer...")
        connection.close()


if __name__ == "__main__":
    main()
