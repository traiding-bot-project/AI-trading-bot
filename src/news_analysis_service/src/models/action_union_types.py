"""Union type definitions for AI service interactions."""

from typing import Annotated

from pydantic import Field

from src.models.ollama_api import (
    OllamaCompletionRequest,
    OllamaCompletionResponse,
    OllamaTagsResponse,
)
from src.models.qwen_api import (
    QwenCompletionRequest,
    QwenCompletionResponse,
    QwenModelsResponse,
)

AnalyzeContentRequest = Annotated[
    OllamaCompletionRequest | QwenCompletionRequest,
    Field(
        ...,
        title="The request for content analysis, which can be any type depending on the AI service used",
    ),
]
AnalyzeContentResponse = Annotated[
    OllamaCompletionResponse | QwenCompletionResponse,
    Field(
        ...,
        title="The response from the content analysis, which can be any type depending on the AI service used",
    ),
]
ListModelsResponse = Annotated[
    OllamaTagsResponse | QwenModelsResponse,
    Field(
        ...,
        title="The response from listing available models, which can be any type depending on the AI service used",
    ),
]
