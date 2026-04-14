"""Interface definitions for AI service interactions."""

from src.interfaces.content_analyzer import AIContentAnalyzer
from src.services import get_ai_service

ai_service = get_ai_service()
content_analyzer = AIContentAnalyzer(service=ai_service)

__all__ = ["content_analyzer"]
