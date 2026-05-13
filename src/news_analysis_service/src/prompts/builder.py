"""Generic prompt builder utilities."""

from pathlib import Path


def load_and_format_prompt(prompt_path: Path, **kwargs) -> str:
    """
    Load a markdown prompt template and format it with the provided keyword arguments.
    
    Args:
        template_name: The name of the template file (e.g., 'analyze_news.md') 
                       located in the same directory as this file.
        **kwargs: The data to format into the template.
        
    Returns:
        The formatted prompt string.
    """
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()
        
    return prompt_template.format(**kwargs)
