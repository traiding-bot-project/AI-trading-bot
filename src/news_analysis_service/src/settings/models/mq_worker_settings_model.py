"""MQWorkerSettings model for RabbitMQ worker configuration."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field

from src.settings.models.custom_base_model import StrictBaseModel


class ExchangeType(StrEnum):
    """Exchange types for RabbitMQ."""

    DIRECT = "direct"
    TOPIC = "topic"
    HEADERS = "headers"
    FANOUT = "fanout"


class MQWorkerConnector(StrictBaseModel):
    """Settings model for RabbitMQ connection parameters."""

    host: Annotated[
        str,
        Field(
            ...,
            title="Host",
            description="Host IP address to bind the service.",
        ),
    ]
    port: Annotated[
        int,
        Field(
            ...,
            ge=1,
            le=65535,
            title="Port",
            description="TCP port to bind the service.",
        ),
    ]
    virtual_host: Annotated[
        str,
        Field(
            ...,
            title="Virtual Host",
            description="RabbitMQ virtual host to connect to.",
        ),
    ]
    heartbeat: Annotated[
        int,
        Field(
            ...,
            ge=0,
            title="Heartbeat",
            description="Heartbeat interval for the RabbitMQ connection.",
        ),
    ]
    socket_timeout: Annotated[
        int,
        Field(
            ...,
            ge=0,
            title="Socket Timeout",
            description="Socket timeout for the RabbitMQ connection.",
        ),
    ]


class MQWorkerExchange(StrictBaseModel):
    """Settings model for RabbitMQ exchange parameters."""

    name: Annotated[
        str,
        Field(
            ...,
            title="Exchange Name",
            description="Name of the RabbitMQ exchange.",
        ),
    ]
    type: Annotated[
        ExchangeType,
        Field(
            ...,
            title="Exchange Type",
            description="Type of the RabbitMQ exchange.",
        ),
    ]
    durable: Annotated[
        bool,
        Field(
            ...,
            title="Durable",
            description="Whether the exchange is durable.",
        ),
    ]
    auto_delete: Annotated[
        bool,
        Field(
            ...,
            title="Auto Delete",
            description="Whether the exchange is auto-deleted.",
        ),
    ]


class MQWorkerQueue(StrictBaseModel):
    """Base settings model for RabbitMQ queue parameters."""

    name: Annotated[
        str,
        Field(
            ...,
            title="Queue Name",
            description="Name of the RabbitMQ queue.",
        ),
    ]
    durable: Annotated[
        bool,
        Field(
            ...,
            title="Durable",
            description="Whether the queue is durable.",
        ),
    ]
    auto_delete: Annotated[
        bool,
        Field(
            ...,
            title="Auto Delete",
            description="Whether the queue is auto-deleted.",
        ),
    ]
    exclusive: Annotated[
        bool,
        Field(
            ...,
            title="Exclusive",
            description="Whether the queue is exclusive.",
        ),
    ]
    routing_key: Annotated[
        str,
        Field(
            ...,
            title="Routing Key",
            description="Routing key for the queue.",
        ),
    ]


class MQWorkerReceiveQueue(MQWorkerQueue):
    """Settings model for RabbitMQ receive queue parameters."""

    prefetch_count: Annotated[
        int,
        Field(
            ...,
            ge=0,
            title="Prefetch Count",
            description="Prefetch count for the receive queue.",
        ),
    ]
    ack: Annotated[
        bool,
        Field(
            ...,
            title="Acknowledge",
            description="Whether to acknowledge messages in the receive queue.",
        ),
    ]


class MQWorkerSendQueue(MQWorkerQueue):
    """Settings model for RabbitMQ send queue parameters."""

    confirm: Annotated[
        bool,
        Field(
            ...,
            title="Confirm",
            description="Whether to confirm messages in the send queue.",
        ),
    ]
    delivery_mode: Annotated[
        int,
        Field(
            default=2,
            ge=1,
            le=2,
            title="Delivery Mode",
            description="Delivery mode for messages (1=transient, 2=persistent).",
        ),
    ]


class MQWorkerSettings(StrictBaseModel):
    """Main settings model for RabbitMQ worker configuration."""

    connector: Annotated[
        MQWorkerConnector,
        Field(
            ...,
            title="Connector",
            description="RabbitMQ connection parameters.",
        ),
    ]
    exchange: Annotated[
        MQWorkerExchange,
        Field(
            ...,
            title="Exchange",
            description="RabbitMQ exchange parameters.",
        ),
    ]
    receive_queues: Annotated[
        list[MQWorkerReceiveQueue],
        Field(
            ...,
            title="Receive Queues",
            description="List of receive queues for the worker.",
        ),
    ]
    send_queues: Annotated[
        list[MQWorkerSendQueue],
        Field(
            ...,
            title="Send Queues",
            description="List of send queues for the worker.",
        ),
    ]
