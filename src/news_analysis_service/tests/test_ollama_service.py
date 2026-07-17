# ruff: noqa: D100, D103
import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
from httpx import Request, Response

from src.models.ai_types import AnalyzeContentRequest
from src.models.ollama_api import OllamaCompletionRequest
from src.settings.models.settings_model import OllamaImplementedEndpoints, OllamaSupportedModels

OLLAMA_MODULE_PATH = Path(__file__).parents[1] / "src" / "services" / "ollama.py"
ollama_spec = importlib.util.spec_from_file_location("ollama_under_test", OLLAMA_MODULE_PATH)

assert ollama_spec is not None
assert ollama_spec.loader is not None

ollama_module = importlib.util.module_from_spec(ollama_spec)
ollama_spec.loader.exec_module(ollama_module)

OllamaService = ollama_module.OllamaService


def make_settings(
    *,
    implemented_endpoints: list[OllamaImplementedEndpoints] | None = None,
    models: list[OllamaSupportedModels] | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        ai_model=SimpleNamespace(
            base_url="http://ollama.local",
            base_port=8080,
            deployments=SimpleNamespace(
                ollama_deployments=SimpleNamespace(
                    api=SimpleNamespace(
                        implemented_endpoints=implemented_endpoints
                        if implemented_endpoints is not None
                        else [OllamaImplementedEndpoints.GENERATE, OllamaImplementedEndpoints.TAGS],
                    ),
                    models=models if models is not None else [OllamaSupportedModels.LLAMA32_1B_Q8_0],
                ),
            ),
        ),
    )


def make_completion_response_payload() -> dict[str, object]:
    return {
        "model": OllamaSupportedModels.LLAMA32_1B_Q8_0.value,
        "created_at": "2026-07-08T10:00:00Z",
        "response": "Semiconductor shares rose after upbeat demand commentary.",
        "done": True,
    }


def make_service_with_client(client: object) -> OllamaService:
    service = OllamaService.__new__(OllamaService)
    service.client = client
    return service


def test_get_endpoint_url_uses_configured_base_url_and_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ollama_module, "settings", make_settings())
    service = OllamaService.__new__(OllamaService)

    url = service.get_endpoint_url(OllamaImplementedEndpoints.GENERATE)

    assert url == "http://ollama.local:8080/api/generate"


def test_get_endpoint_url_rejects_unimplemented_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ollama_module, "settings", make_settings(implemented_endpoints=[]))
    service = OllamaService.__new__(OllamaService)

    with pytest.raises(ValueError, match="not implemented"):
        service.get_endpoint_url(OllamaImplementedEndpoints.GENERATE)


def test_send_get_request_returns_json_response() -> None:
    class FakeClient:
        async def get(self, url: str, headers: dict[str, str]) -> Response:
            assert url == "http://ollama.local:8080/api/tags"
            assert headers == {"Content-Type": "application/json"}
            return Response(200, request=Request("GET", url), json={"models": []})

    service = make_service_with_client(FakeClient())

    response = asyncio.run(service._send_get_request("http://ollama.local:8080/api/tags"))

    assert response == {"models": []}


def test_send_get_request_wraps_http_errors() -> None:
    class FakeClient:
        async def get(self, url: str, headers: dict[str, str]) -> Response:
            return Response(503, request=Request("GET", url), text="unavailable")

    service = make_service_with_client(FakeClient())

    with pytest.raises(RuntimeError, match="Request to Ollama API failed"):
        asyncio.run(service._send_get_request("http://ollama.local:8080/api/tags"))


def test_send_post_request_serializes_body_and_returns_json() -> None:
    class FakeClient:
        async def post(self, url: str, json: dict[str, object], headers: dict[str, str]) -> Response:
            assert url == "http://ollama.local:8080/api/generate"
            assert json["model"] == OllamaSupportedModels.LLAMA32_1B_Q8_0
            assert json["prompt"] == "Analyze this"
            assert headers == {"Content-Type": "application/json"}
            return Response(200, request=Request("POST", url), json={"ok": True})

    service = make_service_with_client(FakeClient())
    body = OllamaCompletionRequest(model=OllamaSupportedModels.LLAMA32_1B_Q8_0, prompt="Analyze this")

    response = asyncio.run(service._send_post_request("http://ollama.local:8080/api/generate", body))

    assert response == {"ok": True}


def test_send_post_request_wraps_http_errors() -> None:
    class FakeClient:
        async def post(self, url: str, json: dict[str, object], headers: dict[str, str]) -> Response:
            return Response(400, request=Request("POST", url), text="bad request body")

    service = make_service_with_client(FakeClient())
    body = OllamaCompletionRequest(model=OllamaSupportedModels.LLAMA32_1B_Q8_0, prompt="Analyze this")

    with pytest.raises(RuntimeError, match="Request to Ollama API failed"):
        asyncio.run(service._send_post_request("http://ollama.local:8080/api/generate", body))


def test_list_models_returns_only_configured_supported_models(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ollama_module, "settings", make_settings())
    service = OllamaService.__new__(OllamaService)

    async def fake_send_get_request(url: str) -> dict[str, object]:
        assert url == "http://ollama.local:8080/api/tags"
        return {
            "models": [
                {
                    "name": "llama3.2:1B-Q8_0",
                    "model": OllamaSupportedModels.LLAMA32_1B_Q8_0.value,
                    "modified_at": "2026-07-08T10:00:00Z",
                    "size": 1234,
                    "digest": "abc123",
                },
                {
                    "name": "unsupported",
                    "model": "unsupported-model",
                    "modified_at": "2026-07-08T10:00:00Z",
                    "size": 5678,
                    "digest": "def456",
                },
            ],
        }

    service._send_get_request = fake_send_get_request

    result = asyncio.run(service.list_models())

    assert result.models == [OllamaSupportedModels.LLAMA32_1B_Q8_0]


def test_generate_completion_builds_ollama_request_and_returns_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ollama_module, "settings", make_settings())
    service = OllamaService.__new__(OllamaService)
    completion_payload = make_completion_response_payload()

    async def fake_send_post_request(url: str, body: OllamaCompletionRequest) -> dict[str, object]:
        assert url == "http://ollama.local:8080/api/generate"
        assert body.model == OllamaSupportedModels.LLAMA32_1B_Q8_0
        assert body.prompt == "Analyze this article"
        return completion_payload

    service._send_post_request = fake_send_post_request

    result = asyncio.run(
        service.generate_completion(
            AnalyzeContentRequest(model=OllamaSupportedModels.LLAMA32_1B_Q8_0, prompt="Analyze this article"),
        ),
    )

    assert result.response == completion_payload["response"]


def test_generate_completion_accepts_model_passed_as_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ollama_module, "settings", make_settings())
    service = OllamaService.__new__(OllamaService)
    completion_payload = make_completion_response_payload()

    async def fake_send_post_request(url: str, body: OllamaCompletionRequest) -> dict[str, object]:
        assert body.model == OllamaSupportedModels.LLAMA32_1B_Q8_0
        return completion_payload

    service._send_post_request = fake_send_post_request

    result = asyncio.run(
        service.generate_completion(
            AnalyzeContentRequest(
                model=OllamaSupportedModels.LLAMA32_1B_Q8_0.value,
                prompt="Analyze this article",
            ),
        ),
    )

    assert result.response == completion_payload["response"]
