"""Generic prompt builder utilities."""

import pathlib


def load_and_format_prompt(template_name: str, **kwargs) -> str:
    """
    Load a markdown prompt template and format it with the provided keyword arguments.
    
    Args:
        template_name: The name of the template file (e.g., 'analyze_news.md') 
                       located in the same directory as this file.
        **kwargs: The data to format into the template.
        
    Returns:
        The formatted prompt string.
    """
    prompt_path = pathlib.Path(__file__).parent / template_name
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()
        
    return prompt_template.format(**kwargs)
