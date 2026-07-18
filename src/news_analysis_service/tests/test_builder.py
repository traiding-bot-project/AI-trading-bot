"""Tests for the prompt template loader (``src.prompts.builder.load_and_format_prompt``).

Covers the shipped news-analysis template plus edge cases around placeholder
substitution, encoding, and error handling using small ad-hoc templates.
"""

import re
from pathlib import Path

import pytest

import src.prompts.builder as builder
from src.constants import ANALYZE_NEWS_PROMPT
from src.models.news_items import DataSourceMetadata, NewsItem, SupportedLanguages
from src.prompts.builder import load_and_format_prompt

SERVICE_ROOT = Path(builder.__file__).parent.parent.parent
PLACEHOLDER = re.compile(r"\{[a-zA-Z_][\w.]*\}")


def _render(tmp_path: Path, template_text: str, **kwargs: object) -> str:
    """To not send entire news analysis prompt."""
    path = tmp_path / "prompt.md"
    path.write_text(template_text, encoding="utf-8")
    return load_and_format_prompt(path, **kwargs)


def test_prompt_formatting() -> None:
    """The shipped prompt template formats with the kwargs the MQ worker actually passes."""
    metadata = DataSourceMetadata(name="Test source", language=SupportedLanguages.POLISH, region="Europe")
    news_item = NewsItem(
        title="Chip stocks rally",
        link="https://test-url",
        description="Semiconductor shares rose after upbeat demand commentary.",
        pub_date="01.01.2025",
        prepared_content="Full article body.",
        metadata=metadata,
    )

    prompt = load_and_format_prompt(
        SERVICE_ROOT / ANALYZE_NEWS_PROMPT,
        news_item=news_item,
        metadata=metadata,
        description=news_item.description,
        prepared_content=news_item.prepared_content,
    )

    assert news_item.title in prompt
    assert news_item.link in prompt
    assert "Test source" in prompt
    assert "Full article body." in prompt
    assert '{ "impact": "No material market implication."' in prompt


def test_values_containing_braces_are_not_reformatted(tmp_path: Path) -> None:
    """Braces inside a substituted value are treated as literals, not re-expanded.

    A single substitution pass must not recurse into the injected text, so an
    unrelated ``{equity_sectors_list}`` token carried in by the value survives
    verbatim instead of triggering a second lookup.
    """
    noisy = 'leftover json {"a": 1} and a placeholder {equity_sectors_list}'
    out = _render(tmp_path, "{prepared_content}", prepared_content=noisy)
    assert out == noisy


def test_template_is_read_as_utf8(tmp_path: Path) -> None:
    """The template file is decoded as UTF-8 so non-ASCII characters round-trip."""
    out = _render(tmp_path, "Zażółć gęślą jaźń: {description}", description="opis")
    assert out == "Zażółć gęślą jaźń: opis"


def test_missing_template_raises_file_not_found(tmp_path: Path) -> None:
    """Pointing at a non-existent template path raises ``FileNotFoundError``."""
    with pytest.raises(FileNotFoundError):
        load_and_format_prompt(tmp_path / "does_not_exist.md")


def test_missing_kwarg_raises_key_error_naming_the_placeholder(tmp_path: Path) -> None:
    """A placeholder with no matching kwarg raises ``KeyError`` naming the placeholder."""
    with pytest.raises(KeyError, match="description"):
        _render(tmp_path, "{description}")


def test_filter_kwarg_collides_with_injected_value(tmp_path: Path) -> None:
    """A caller kwarg that reuses an internally injected name raises ``TypeError``.

    ``special`` is supplied by the loader itself, so passing it again produces a
    "multiple values for keyword argument" error rather than being silently used.
    """
    with pytest.raises(TypeError, match="multiple values"):
        _render(tmp_path, "anything", special="mine")


def test_unused_kwargs_are_ignored(tmp_path: Path) -> None:
    """Extra kwargs with no matching placeholder are ignored, leaving the text unchanged."""
    assert _render(tmp_path, "hello", unused="x") == "hello"
