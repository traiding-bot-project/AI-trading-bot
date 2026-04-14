"""Union types for AI service interactions."""

from typing import Annotated

from pydantic import Field

from src.models.ollama_api import OllamaCompletionRequest, OllamaCompletionResponse, OllamaTagsResponse

AnalyzeContentRequest = Annotated[
    OllamaCompletionRequest,
    Field(
        ...,
        title="The request for content analysis, which can be any type depending on the AI service used",
    ),
]
AnalyzeContentResponse = Annotated[
    OllamaCompletionResponse,
    Field(
        ...,
        title="The response from the content analysis, which can be any type depending on the AI service used",
    ),
]
ListModelsResponse = Annotated[
    OllamaTagsResponse,
    Field(
        ...,
        title="The response from listing available models, which can be any type depending on the AI service used",
    ),
]
