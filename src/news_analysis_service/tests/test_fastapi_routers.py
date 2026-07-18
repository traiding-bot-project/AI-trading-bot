"""Tests for the FastAPI HTTP layer (health check and the qwen/ollama generate routes).

The content analyzers are replaced with ``AsyncMock`` dependency overrides so the
tests exercise routing, request validation, and response shaping without hitting a
real model backend.
"""
from collections.abc import Iterator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

import src.analyzer  # noqa: F401  # imported first to resolve the analyzer<->services circular import
from fastapi import status
from src.fastapi.app import app
from src.fastapi.ollama import get_ollama_content_analyzer
from src.fastapi.qwen import get_qwen_content_analyzer
from src.models.ai_types import AnalyzeContentResponse

QWEN_MODEL = "docker.io/ai/qwen3:8B-Q4_K_M"
OLLAMA_MODEL = "docker.io/ai/llama3.2:1B-Q8_0"


@pytest.fixture
def qwen_analyzer() -> AsyncMock:
    """A stub Qwen content analyzer returning a fixed ``"qwen-response"`` payload."""
    analyzer = AsyncMock()
    analyzer.analyze_content.return_value = AnalyzeContentResponse(response="qwen-response")
    return analyzer


@pytest.fixture
def ollama_analyzer() -> AsyncMock:
    """A stub Ollama content analyzer returning a fixed ``"ollama-response"`` payload."""
    analyzer = AsyncMock()
    analyzer.analyze_content.return_value = AnalyzeContentResponse(response="ollama-response")
    return analyzer


@pytest.fixture
def client(qwen_analyzer: AsyncMock, ollama_analyzer: AsyncMock) -> Iterator[TestClient]:
    """A ``TestClient`` with the qwen/ollama analyzer dependencies overridden by stubs.

    Overrides are registered before the client starts and cleared on teardown so
    tests stay isolated from each other and from the real analyzer dependencies.
    """
    app.dependency_overrides[get_qwen_content_analyzer] = lambda: qwen_analyzer
    app.dependency_overrides[get_ollama_content_analyzer] = lambda: ollama_analyzer
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_returns_200(client: TestClient) -> None:
    """``GET /health`` returns 200 with the ``{"status": "OK"}`` body."""
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "OK"}


def test_qwen_generate_hits_analyzer_and_returns_response(
    client: TestClient, qwen_analyzer: AsyncMock
) -> None:
    """``POST /api/qwen/generate`` forwards model and prompt to the analyzer and returns its response.

    Also asserts the analyzer was awaited exactly once with a request carrying the
    submitted model and prompt.
    """
    response = client.post(
        "/api/qwen/generate",
        json={"model": QWEN_MODEL, "prompt": "analyse this"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"response": "qwen-response"}

    qwen_analyzer.analyze_content.assert_awaited_once()
    request = qwen_analyzer.analyze_content.await_args.args[0]
    assert request.model == QWEN_MODEL
    assert request.prompt == "analyse this"


def test_ollama_generate_hits_analyzer_and_returns_response(
    client: TestClient, ollama_analyzer: AsyncMock
) -> None:
    """``POST /api/ollama/generate`` forwards model and prompt to the analyzer and returns its response.

    Also asserts the analyzer was awaited exactly once with a request carrying the
    submitted model and prompt.
    """
    response = client.post(
        "/api/ollama/generate",
        json={"model": OLLAMA_MODEL, "prompt": "analyse this"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"response": "ollama-response"}

    ollama_analyzer.analyze_content.assert_awaited_once()
    request = ollama_analyzer.analyze_content.await_args.args[0]
    assert request.model == OLLAMA_MODEL
    assert request.prompt == "analyse this"


def test_qwen_generate_missing_prompt_returns_422(client: TestClient, qwen_analyzer: AsyncMock) -> None:
    """A qwen request without the required ``prompt`` field is rejected with 422 before the analyzer runs."""
    response = client.post("/api/qwen/generate", json={"model": QWEN_MODEL})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    qwen_analyzer.analyze_content.assert_not_awaited()


def test_qwen_generate_rejects_non_qwen_model(client: TestClient, qwen_analyzer: AsyncMock) -> None:
    """The qwen route rejects a non-qwen model with 422 and never invokes the analyzer."""
    response = client.post(
        "/api/qwen/generate",
        json={"model": OLLAMA_MODEL, "prompt": "analyse this"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    qwen_analyzer.analyze_content.assert_not_awaited()


def test_ollama_generate_missing_prompt_returns_422(client: TestClient, ollama_analyzer: AsyncMock) -> None:
    """An ollama request without the required ``prompt`` field is rejected with 422 before the analyzer runs."""
    response = client.post("/api/ollama/generate", json={"model": OLLAMA_MODEL})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    ollama_analyzer.analyze_content.assert_not_awaited()


def test_ollama_generate_rejects_non_ollama_model(client: TestClient, ollama_analyzer: AsyncMock) -> None:
    """The ollama route rejects a non-ollama model with 422 and never invokes the analyzer."""
    response = client.post(
        "/api/ollama/generate",
        json={"model": QWEN_MODEL, "prompt": "analyse this"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    ollama_analyzer.analyze_content.assert_not_awaited()
