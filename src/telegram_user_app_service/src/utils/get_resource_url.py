"""Utility functions for constructing resource URLs with authentication."""


def get_resource_url(
    url_schema: str,
    host: str,
    port: int,
    username: str | None = None,
    password: str | None = None,
    api: str | None = None,
) -> str:
    """Construct a complete resource URL with optional authentication credentials."""
    auth = ""
    if username:
        auth = f"{username}{f':{password}' if password else ''}@"

    path = f"/{api}" if api else ""

    return f"{url_schema}://{auth}{host}:{port}{path}"
