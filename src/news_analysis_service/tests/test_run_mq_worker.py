"""Tests for the RabbitMQ worker entrypoint (``src/scripts/run_mq_worker.py``).

``main()`` is driven with mocked settings, connection, and analyzer just far enough
to capture the ``on_message`` consumer callback, which is then exercised directly to
verify the analyze-then-publish flow and error handling on a malformed message body.
"""

import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import src.scripts.run_mq_worker as worker
from src.models.ai_types import AnalyzeContentResponse


def _make_settings() -> MagicMock:
    """Minimal stand-in for the MQWorkerSettings object main() consumes."""
    s = MagicMock()
    s.connector.host, s.connector.port = "localhost", 5672
    s.connector.virtual_host, s.connector.heartbeat = "/", 60
    s.exchange.name, s.exchange.type.value = "news", "direct"
    s.exchange.durable, s.exchange.auto_delete = True, False

    recv = MagicMock(
        name="in", durable=True, auto_delete=False, exclusive=False, routing_key="in.key", prefetch_count=1
    )
    send = MagicMock(
        name="out", durable=True, auto_delete=False, exclusive=False, routing_key="out.key", delivery_mode=2
    )
    s.receive_queues, s.send_queues = [recv], [send]
    return s


class _FakeMessage:
    """Supports `message.body` and `async with message.process(requeue=False):`."""

    def __init__(self, body: bytes) -> None:
        self.body = body

    @asynccontextmanager
    async def process(self, requeue: bool = False) -> AsyncIterator[_FakeMessage]:
        yield self


async def _drive_main_and_capture_callback(
    settings_mock: MagicMock,
    analyzer: AsyncMock,
    exchange: AsyncMock,
    queue: AsyncMock,
) -> Any:
    """Run main() far enough to register on_message, then cancel and return it."""
    connection = AsyncMock()
    channel = AsyncMock()
    connection.channel.return_value = channel
    channel.declare_exchange.return_value = exchange
    channel.declare_queue.return_value = queue
    channel.get_queue.return_value = queue

    with (
        patch.object(worker, "load_settings", return_value=settings_mock),
        patch.object(worker, "connect_robust", AsyncMock(return_value=connection)),
        patch.object(worker, "configure_logging"),
        patch.object(worker, "get_compatible_api_for_model"),
        patch.object(worker, "get_content_analyzer", return_value=analyzer),
        patch.object(worker, "load_and_format_prompt", return_value="PROMPT"),
    ):
        task = asyncio.create_task(worker.main())
        await asyncio.sleep(0.05)  # let main() reach the infinite-future await
        task.cancel()
        await task  # main() catches CancelledError and returns

    return queue.consume.call_args.args[0]  # the on_message closure


def test_on_message_analyzes_and_publishes() -> None:
    """A valid message is analyzed and the result republished with the worker's mutations applied.

    Asserts the analyzer is awaited once and the published body carries the analysis
    response, a cleared ``prepared_content``, and the model name stamped into metadata.
    """

    async def scenario() -> None:
        settings_mock = _make_settings()
        exchange, queue = AsyncMock(), AsyncMock()

        analyzer = AsyncMock()
        analyzer.analyze_content.return_value = AnalyzeContentResponse(response="RESULT")

        on_message = await _drive_main_and_capture_callback(settings_mock, analyzer, exchange, queue)

        incoming = {
            "title": "ACME beats earnings",
            "link": "https://example.com/acme",
            "description": "Strong Q3",
            "pub_date": "2026-07-18",
            "prepared_content": "full article text",
            "metadata": {"name": "PAP", "language": "pl", "region": "pl"},
        }
        await on_message(_FakeMessage(json.dumps(incoming).encode("utf-8")))

        # analyzer was invoked
        analyzer.analyze_content.assert_awaited_once()

        # results were published, with the mutations applied
        exchange.publish.assert_awaited_once()
        published_message = exchange.publish.call_args.args[0]
        body = json.loads(published_message.body)
        assert body["response"] == "RESULT"
        assert body["prepared_content"] is None
        assert body["metadata"]["model_used"] == worker.USER_MODEL

    asyncio.run(scenario())


def test_on_message_reraises_on_invalid_body() -> None:
    """A non-JSON message body causes ``on_message`` to raise without analyzing or publishing."""

    async def scenario() -> None:
        settings_mock = _make_settings()
        exchange, queue = AsyncMock(), AsyncMock()
        analyzer = AsyncMock()

        on_message = await _drive_main_and_capture_callback(settings_mock, analyzer, exchange, queue)

        with pytest.raises(Exception):  # noqa: B017, PT011
            await on_message(_FakeMessage(b"not json"))

        analyzer.analyze_content.assert_not_awaited()
        exchange.publish.assert_not_awaited()

    asyncio.run(scenario())
