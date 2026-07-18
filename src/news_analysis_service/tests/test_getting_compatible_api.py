"""Tests for ``src.analyzer.get_compatible_api_for_model``.

Verifies that a model name is mapped to the ``CompatibleAPI`` provider that
supports it, and that an unknown model is rejected.
"""

from types import SimpleNamespace

import pytest

from src.analyzer import get_compatible_api_for_model
from src.settings.models.settings_model import CompatibleAPI, QwenImplementedEndpoints, QwenSupportedModels


def make_settings(
    *,
    implemented_endpoints: list[QwenImplementedEndpoints] | None = None,
    models: list[QwenSupportedModels] | None = None,
) -> SimpleNamespace:
    """Build a minimal settings stand-in exposing the qwen deployment's endpoints and models."""
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


def test_get_compatible_api_for_model() -> None:
    """A supported Qwen model resolves to the ``CompatibleAPI.QWEN`` provider."""
    api = get_compatible_api_for_model(model_name=QwenSupportedModels.QWEN3_8B_Q4_K_M)
    assert api == CompatibleAPI.QWEN


def test_get_compatible_api_for_model_unknown_raises() -> None:
    """A model name not configured for any provider raises ``ValueError``."""
    with pytest.raises(ValueError, match="is not supported by any configured API provider"):
        get_compatible_api_for_model(model_name="docker.io/ai/nonexistent:1B")  # type: ignore[arg-type]


def test_returns_compatible_api_enum_instance() -> None:
    """The lookup returns a ``CompatibleAPI`` enum member rather than a bare string."""
    api = get_compatible_api_for_model(model_name=QwenSupportedModels.QWEN3_8B_Q4_K_M)
    assert isinstance(api, CompatibleAPI)
