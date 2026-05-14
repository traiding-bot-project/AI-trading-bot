"""Generic prompt builder utilities."""

from pathlib import Path
from typing import Any


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

    return prompt_template.format(**kwargs)
