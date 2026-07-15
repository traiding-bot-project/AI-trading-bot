import re
from pathlib import Path

import pytest

import src.prompts.builder as builder
from src.prompts.builder import load_and_format_prompt
from src.models.news_items import NewsItem, DataSourceMetadata, SupportedLanguages
from src.constants import ANALYZE_NEWS_PROMPT


SERVICE_ROOT = Path(builder.__file__).parent.parent.parent
PLACEHOLDER = re.compile(r"\{[a-zA-Z_][\w.]*\}")


def _render(tmp_path: Path, template_text: str, **kwargs: object) -> str:
    """To not send entire news analysis prompt."""
    path = tmp_path / "prompt.md"
    path.write_text(template_text, encoding="utf-8")
    return load_and_format_prompt(path, **kwargs)


def test_prompt_formatting():
    """The shipped prompt template formats with the kwargs the MQ worker actually passes."""
    metadata = DataSourceMetadata(
        name = "Test source",
        language = SupportedLanguages.POLISH,
        region = "Europe"
    )
    news_item = NewsItem(
        title = "Chip stocks rally",
        link = "https://test-url",
        description = "Semiconductor shares rose after upbeat demand commentary.",
        pub_date = "01.01.2025",
        prepared_content="Full article body.",
        metadata = metadata
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
    noisy = 'leftover json {"a": 1} and a placeholder {equity_sectors_list}'
    out = _render(tmp_path, "{prepared_content}", prepared_content=noisy)
    assert out == noisy


def test_template_is_read_as_utf8(tmp_path: Path) -> None:
    out = _render(tmp_path, "Zażółć gęślą jaźń: {description}", description="opis")
    assert out == "Zażółć gęślą jaźń: opis"


def test_missing_template_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_and_format_prompt(tmp_path / "does_not_exist.md")


def test_missing_kwarg_raises_key_error_naming_the_placeholder(tmp_path: Path) -> None:
    with pytest.raises(KeyError, match="description"):
        _render(tmp_path, "{description}")


def test_filter_kwarg_collides_with_injected_value(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="multiple values"):
        _render(tmp_path, "anything", special="mine")


def test_unused_kwargs_are_ignored(tmp_path: Path) -> None:
    assert _render(tmp_path, "hello", unused="x") == "hello"
