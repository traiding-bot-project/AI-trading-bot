"""Union type definitions for AI service interactions."""

from typing import Annotated, Union

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
    Union[OllamaCompletionRequest, QwenCompletionRequest],
    Field(
        ...,
        title="The request for content analysis, which can be any type depending on the AI service used",
    ),
]
AnalyzeContentResponse = Annotated[
    Union[OllamaCompletionResponse, QwenCompletionResponse],
    Field(
        ...,
        title="The response from the content analysis, which can be any type depending on the AI service used",
    ),
]
ListModelsResponse = Annotated[
    Union[OllamaTagsResponse, QwenModelsResponse],
    Field(
        ...,
        title="The response from listing available models, which can be any type depending on the AI service used",
    ),
]
