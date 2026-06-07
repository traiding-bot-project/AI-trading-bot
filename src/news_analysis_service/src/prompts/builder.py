"""Generic prompt builder utilities."""

from pathlib import Path
from typing import Any, get_args

from src.models.analysis_filters import (
    asset_classes_and_macro_themes_list,
    commodities_list,
    equity_sectors_list,
    special,
)


def load_and_format_prompt(prompt_path: Path, **kwargs: Any) -> str:
    """Load a markdown prompt template and format it with the provided keyword arguments.

    Args:
        prompt_path: The path to the markdown template file.
        **kwargs: The data to format into the template.

    Returns:
        The formatted prompt string.
    """
    with open(prompt_path, encoding="utf-8") as f:
        prompt_template = f.read()

    clean_equity = ", ".join(f"'{str(x)}'" for x in get_args(equity_sectors_list))
    clean_commodities = ", ".join(f"'{str(x)}'" for x in get_args(commodities_list))
    clean_macro = ", ".join(f"'{str(x)}'" for x in get_args(asset_classes_and_macro_themes_list))
    clean_special = ", ".join(f"'{str(x)}'" for x in get_args(special))

    return prompt_template.format(
        equity_sectors_list=clean_equity,
        commodities_list=clean_commodities,
        asset_classes_and_macro_themes_list=clean_macro,
        special=clean_special,
        **kwargs,
    )
