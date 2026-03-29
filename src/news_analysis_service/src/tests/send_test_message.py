"""Test script to send a message to the news analysis microservice via RabbitMQ."""

import json

from pika import BlockingConnection, ConnectionParameters


def main() -> None:
    """Send a test message to the news analysis tasks queue."""
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

    # Declare the tasks queue (in case it's not already declared)
    channel.queue_declare(
        queue="news_analysis_tasks",
        durable=True,
        auto_delete=False,
        exclusive=False,
    )
    channel.queue_bind(
        queue="news_analysis_tasks",
        exchange="news_analysis",
        routing_key="tasks",
    )

    # Sample request data
    request_data = {
        "model": "docker.io/ai/llama3.2:1B-Q8_0",
        "prompt": "Analyze the text and provide insights on what will be the impact on the Orlen stock. Title: Venture Global discusses settling pending arbitration cases with energy companies Text: Venture Global is holding discussions to settle pending arbitration cases with energy companies that sued the firm for failing to provide them with LNG from its Calcasieu Pass facility in a timely manner, CEO Mike Sabel said on Monday during a roundtable discussion at the CERAWeek conference in Houston. Venture Global customers including Shell, BP, Repsol, Orlen, and Edison filed arbitration cases in 2023 after accusing Venture Global of failing to provide them with LNG for more than two years after it first produced the superchilled gas. BP won its case against Venture Global, while the LNG exporter won its cases against Shell and Repsol. The other cases have not been concluded. Sabel said while Venture Global won two of its arbitration cases and lost one, it is open to settling the remaining arbitration cases. Venture Global expects to produce LNG from its CP2 facility at 150% of the 20 million metric tons per annum nameplate capacity, he said, adding the company wants to sell more LNG cargoes on five-year contracts while the plant is being commissioned. The company could add 40 million mtpa of LNG from proposed expansions to its Plaquemines and CP2 plants, Sabel said. Sabel said that even though the company has been granted permission by the U.S. Department of Energy to increase its LNG exports, he does not expect any more production than what was already planned for the rest of the year.",
        "stream": False,
    }

    # Publish the message
    channel.basic_publish(
        exchange="news_analysis",
        routing_key="tasks",
        body=json.dumps(request_data),
    )

    print("Test message sent to news_analysis_tasks queue.")

    connection.close()


if __name__ == "__main__":
    main()
