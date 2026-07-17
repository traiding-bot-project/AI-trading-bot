# ruff: noqa: D100, D103
from types import SimpleNamespace

import pytest

import src.analyzer  # noqa: F401  # imported first to resolve the analyzer<->services circular import
import src.services as ai_service_factory
from src.services import QwenService, get_ai_service
from src.settings.models.settings_model import CompatibleAPI


def make_settings(*configured_apis: CompatibleAPI) -> SimpleNamespace:
    deployments = [
        (api.value, SimpleNamespace(api=SimpleNamespace(compatible_api=api))) for api in configured_apis
    ]
    return SimpleNamespace(ai_model=SimpleNamespace(deployments=deployments))


def test_returns_service_instance_for_configured_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai_service_factory, "settings", make_settings(CompatibleAPI.QWEN))

    service = get_ai_service(CompatibleAPI.QWEN)

    assert isinstance(service, QwenService)


def test_raises_value_error_for_unconfigured_api(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai_service_factory, "settings", make_settings(CompatibleAPI.QWEN))

    with pytest.raises(ValueError, match="Unsupported compatible API provider"):
        get_ai_service(CompatibleAPI.OLLAMA)
