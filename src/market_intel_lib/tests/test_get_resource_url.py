"""Tests for ``market_intel_lib.utils.get_resource_url.get_resource_url``.

Covers each branch of the URL builder: no auth, username-only, username with
password, an optional API path, and the edge case where a password is supplied
without a username (the password is silently dropped).
"""

from market_intel_lib.utils.get_resource_url import get_resource_url


def test_host_and_port_only() -> None:
    """With no credentials or path, the URL is just schema://host:port."""
    url = get_resource_url(url_schema="postgresql", host="localhost", port=5432)

    assert url == "postgresql://localhost:5432"


def test_username_without_password() -> None:
    """A username without a password produces user@host with no colon."""
    url = get_resource_url(
        url_schema="postgresql", host="localhost", port=5432, username="admin"
    )

    assert url == "postgresql://admin@localhost:5432"


def test_username_with_password() -> None:
    """A username and password produce user:pass@host."""
    url = get_resource_url(
        url_schema="postgresql",
        host="localhost",
        port=5432,
        username="admin",
        password="secret",
    )

    assert url == "postgresql://admin:secret@localhost:5432"


def test_api_path_appended() -> None:
    """An api value is appended as a trailing /api segment."""
    url = get_resource_url(
        url_schema="http", host="localhost", port=8080, api="v1/health"
    )

    assert url == "http://localhost:8080/v1/health"


def test_password_without_username_is_dropped() -> None:
    """A password with no username is silently ignored (auth requires a username)."""
    url = get_resource_url(
        url_schema="postgresql", host="localhost", port=5432, password="secret"
    )

    assert url == "postgresql://localhost:5432"


def test_all_options_combined() -> None:
    """Username, password, and api combine into a full authenticated URL with path."""
    url = get_resource_url(
        url_schema="https",
        host="example.com",
        port=443,
        username="admin",
        password="secret",
        api="api/v2",
    )

    assert url == "https://admin:secret@example.com:443/api/v2"
