"""Tests for ``QwenService`` (``src/services/qwen.py``).

The module is loaded in isolation via ``importlib`` so ``settings`` can be
monkeypatched per test. Covers endpoint URL building, GET/POST request helpers
(including HTTP-error wrapping), model listing, and completion generation with the
OpenAI-style chat schema — including parsing the structured JSON response and
rejecting a non-JSON model reply. HTTP is faked in memory; no network calls.
"""

import asyncio
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from httpx import Request, Response

from src.models.ai_types import AnalyzeContentRequest
from src.models.qwen_api import ChatMessage, ChatMessageRole, QwenCompletionRequest
from src.settings.models.settings_model import QwenImplementedEndpoints, QwenSupportedModels

QWEN_MODULE_PATH = Path(__file__).parents[1] / "src" / "services" / "qwen.py"
qwen_spec = importlib.util.spec_from_file_location("qwen_under_test", QWEN_MODULE_PATH)

assert qwen_spec is not None
assert qwen_spec.loader is not None

qwen_module = importlib.util.module_from_spec(qwen_spec)
qwen_spec.loader.exec_module(qwen_module)

QwenService = qwen_module.QwenService


def make_settings(
    *,
    implemented_endpoints: list[QwenImplementedEndpoints] | None = None,
    models: list[QwenSupportedModels] | None = None,
) -> SimpleNamespace:
    """Build a settings stand-in exposing the qwen deployment's endpoints and models."""
    return SimpleNamespace(
        ai_model=SimpleNamespace(
            base_url="http://qwen.local",
            base_port=8080,
            deployments=SimpleNamespace(
                qwen_deployments=SimpleNamespace(
                    api=SimpleNamespace(
                        implemented_endpoints=implemented_endpoints
                        if implemented_endpoints is not None
                        else [QwenImplementedEndpoints.CHAT_COMPLETIONS, QwenImplementedEndpoints.MODELS],
                    ),
                    models=models if models is not None else [QwenSupportedModels.QWEN3_8B_Q4_K_M],
                ),
            ),
        ),
    )


def make_structured_response_payload() -> dict[str, object]:
    """Return a representative structured news-analysis payload the model is expected to emit."""
    return {
        "title": "Chip stocks rally",
        "source": "Market Wire",
        "published_at": "2026-07-08T10:00:00Z",
        "summary": "Semiconductor shares rose after upbeat demand commentary.",
        "market_takeaways": [
            {
                "impact": "Semiconductor suppliers may see stronger near-term demand.",
                "sector": "Semiconductors",
                "sentiment": "positive",
            },
        ],
        "mentioned_companies": ["Example Semi"],
        "affected_sectors": ["Semiconductors", "Technology"],
        "significance": "high",
    }


def make_service_with_client(client: object) -> Any:
    """Construct a ``QwenService`` without running ``__init__``, wiring in a fake HTTP client.

    Returns ``Any`` because the service class is loaded dynamically via ``importlib`` and
    the tests deliberately stub its private request helpers.
    """
    service = QwenService.__new__(QwenService)
    service.client = client
    return service


def test_get_endpoint_url_uses_configured_base_url_and_port(monkeypatch: pytest.MonkeyPatch) -> None:
    """An endpoint URL is assembled from the configured base URL, port, and endpoint path."""
    monkeypatch.setattr(qwen_module, "settings", make_settings())
    service = QwenService.__new__(QwenService)

    url = service.get_endpoint_url(QwenImplementedEndpoints.CHAT_COMPLETIONS)

    assert url == "http://qwen.local:8080/v1/chat/completions"


def test_get_endpoint_url_rejects_unimplemented_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    """Requesting a URL for an endpoint not in the configured list raises ``ValueError``."""
    monkeypatch.setattr(qwen_module, "settings", make_settings(implemented_endpoints=[]))
    service = QwenService.__new__(QwenService)

    with pytest.raises(ValueError, match="not implemented"):
        service.get_endpoint_url(QwenImplementedEndpoints.CHAT_COMPLETIONS)


def test_send_get_request_returns_json_response() -> None:
    """``_send_get_request`` issues the GET with JSON headers and returns the decoded body."""

    class FakeClient:
        async def get(self, url: str, headers: dict[str, str]) -> Response:
            assert url == "http://qwen.local:8080/v1/models"
            assert headers == {"Content-Type": "application/json"}
            return Response(200, request=Request("GET", url), json={"object": "list", "data": []})

    service = make_service_with_client(FakeClient())

    response = asyncio.run(service._send_get_request("http://qwen.local:8080/v1/models"))

    assert response == {"object": "list", "data": []}


def test_send_get_request_wraps_http_errors() -> None:
    """A non-2xx GET response is re-raised as a ``RuntimeError`` describing the failure."""

    class FakeClient:
        async def get(self, url: str, headers: dict[str, str]) -> Response:
            return Response(503, request=Request("GET", url), text="unavailable")

    service = make_service_with_client(FakeClient())

    with pytest.raises(RuntimeError, match="Request to Qwen API failed"):
        asyncio.run(service._send_get_request("http://qwen.local:8080/v1/models"))


def test_send_post_request_serializes_body_and_returns_json() -> None:
    """``_send_post_request`` serializes the chat request to JSON and returns the decoded response."""

    class FakeClient:
        async def post(self, url: str, json: dict[str, object], headers: dict[str, str]) -> Response:
            assert url == "http://qwen.local:8080/v1/chat/completions"
            assert json["model"] == QwenSupportedModels.QWEN3_8B_Q4_K_M
            assert json["messages"] == [{"role": ChatMessageRole.USER, "content": "Analyze this"}]
            assert headers == {"Content-Type": "application/json"}
            return Response(200, request=Request("POST", url), json={"ok": True})

    service = make_service_with_client(FakeClient())
    body = QwenCompletionRequest(
        model=QwenSupportedModels.QWEN3_8B_Q4_K_M,
        messages=[ChatMessage(role=ChatMessageRole.USER, content="Analyze this")],
    )

    response = asyncio.run(service._send_post_request("http://qwen.local:8080/v1/chat/completions", body))

    assert response == {"ok": True}


def test_send_post_request_includes_response_text_in_wrapped_http_errors() -> None:
    """A non-2xx POST is re-raised as ``RuntimeError`` whose message includes the server's response text."""

    class FakeClient:
        async def post(self, url: str, json: dict[str, object], headers: dict[str, str]) -> Response:
            return Response(400, request=Request("POST", url), text="bad request body")

    service = make_service_with_client(FakeClient())
    body = QwenCompletionRequest(
        model=QwenSupportedModels.QWEN3_8B_Q4_K_M,
        messages=[ChatMessage(role=ChatMessageRole.USER, content="Analyze this")],
    )

    with pytest.raises(RuntimeError, match="bad request body"):
        asyncio.run(service._send_post_request("http://qwen.local:8080/v1/chat/completions", body))


def test_list_models_returns_only_configured_supported_models(monkeypatch: pytest.MonkeyPatch) -> None:
    """``list_models`` filters the ``/v1/models`` response down to the configured supported models."""
    monkeypatch.setattr(qwen_module, "settings", make_settings())
    service = QwenService.__new__(QwenService)

    async def fake_send_get_request(url: str) -> dict[str, object]:
        assert url == "http://qwen.local:8080/v1/models"
        return {
            "object": "list",
            "data": [
                {
                    "id": QwenSupportedModels.QWEN3_8B_Q4_K_M.value,
                    "object": "model",
                    "created": 1,
                    "owned_by": "qwen",
                },
                {
                    "id": "unsupported-model",
                    "object": "model",
                    "created": 1,
                    "owned_by": "qwen",
                },
            ],
        }

    service._send_get_request = fake_send_get_request

    result = asyncio.run(service.list_models())

    assert result.models == [QwenSupportedModels.QWEN3_8B_Q4_K_M]


def test_generate_completion_builds_qwen_request_and_parses_structured_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``generate_completion`` sends a json_schema-constrained chat request and parses the structured reply.

    The faked backend returns the assistant message as a JSON string; the service
    must decode it into the typed news-analysis response (title, market takeaways,
    affected sectors, etc.).
    """
    monkeypatch.setattr(qwen_module, "settings", make_settings())
    service = QwenService.__new__(QwenService)
    structured_payload = make_structured_response_payload()

    async def fake_send_post_request(url: str, body: QwenCompletionRequest) -> dict[str, object]:
        assert url == "http://qwen.local:8080/v1/chat/completions"
        assert body.model == QwenSupportedModels.QWEN3_8B_Q4_K_M
        assert body.messages[0].role == ChatMessageRole.USER
        assert body.messages[0].content == "Analyze this article"
        assert body.response_format is not None
        assert body.response_format["type"] == "json_schema"
        return {
            "id": "completion-1",
            "object": "chat.completion",
            "created": 1,
            "model": QwenSupportedModels.QWEN3_8B_Q4_K_M.value,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": json.dumps(structured_payload)},
                    "finish_reason": "stop",
                },
            ],
        }

    service._send_post_request = fake_send_post_request

    result = asyncio.run(
        service.generate_completion(
            AnalyzeContentRequest(model=QwenSupportedModels.QWEN3_8B_Q4_K_M, prompt="Analyze this article"),
        ),
    )

    assert result.response.title == structured_payload["title"]
    assert result.response.market_takeaways[0].sector == "Semiconductors"
    assert result.response.affected_sectors == ["Semiconductors", "Technology"]


def test_generate_completion_raises_value_error_when_model_response_is_not_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the model returns non-JSON content, ``generate_completion`` raises ``ValueError``."""
    monkeypatch.setattr(qwen_module, "settings", make_settings())
    service = QwenService.__new__(QwenService)

    async def fake_send_post_request(url: str, body: QwenCompletionRequest) -> dict[str, object]:
        return {
            "id": "completion-1",
            "object": "chat.completion",
            "created": 1,
            "model": QwenSupportedModels.QWEN3_8B_Q4_K_M.value,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "not json"},
                    "finish_reason": "stop",
                },
            ],
        }

    service._send_post_request = fake_send_post_request

    with pytest.raises(ValueError, match="not valid JSON"):
        asyncio.run(
            service.generate_completion(
                AnalyzeContentRequest(model=QwenSupportedModels.QWEN3_8B_Q4_K_M, prompt="Analyze this article"),
            ),
        )
