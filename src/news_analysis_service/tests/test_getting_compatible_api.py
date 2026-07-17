from types import SimpleNamespace

from src.analyzer import get_compatible_api_for_model
from src.settings.models.settings_model import (
    QwenSupportedModels,
    QwenImplementedEndpoints,
    CompatibleAPI
)


def make_settings(
    *,
    implemented_endpoints: list[QwenImplementedEndpoints] | None = None,
    models: list[QwenSupportedModels] | None = None,
) -> SimpleNamespace:
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

    api = get_compatible_api_for_model(model_name=QwenSupportedModels.QWEN3_8B_Q4_K_M)
    assert api == CompatibleAPI.QWEN
