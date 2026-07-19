"""Tests for the pure helpers of ``market_intel_lib.utils.file_storage``.

Covers the S3-free logic: remote key construction, metadata normalisation, MD5
hashing (string and file), and the duplicate-detection branch logic with a
mocked S3 client. No network or S3 backend is exercised.
"""

import asyncio
import hashlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock

from botocore.exceptions import ClientError

from market_intel_lib.utils.file_storage import (
    FileStorageFolder,
    FileStorageService,
)

# md5 of b"hello", used across the hashing and duplicate-detection tests.
HELLO_MD5 = "5d41402abc4b2a76b9719d911017c592"


def _patch_client(service: FileStorageService, client: object) -> None:
    """Replace the service's ``_get_client`` with one yielding the given mock client."""

    @asynccontextmanager
    async def _cm() -> AsyncIterator[object]:
        yield client

    service._get_client = _cm  # type: ignore[assignment]


def _client_error(code: str) -> ClientError:
    """Build a botocore ClientError carrying the given error code."""
    return ClientError({"Error": {"Code": code}}, "HeadObject")


def test_create_remote_object_name_joins_folder_and_name() -> None:
    """The remote key is the folder value joined to the object name with a slash."""
    result = FileStorageService.create_remote_object_name(
        FileStorageFolder.RAW_NEWS, "article.txt"
    )

    assert result == "raw-news/article.txt"


def test_handle_file_metadata_normalises_keys_and_quotes_values() -> None:
    """Keys are lowercased with spaces turned into dashes; values are URL-quoted."""
    service = FileStorageService()

    result = service._handle_file_metadata(
        {"Source Name": "New York Times", "URL": "http://example.com/a b"}
    )

    assert result == {
        "source-name": "New%20York%20Times",
        "url": "http%3A//example.com/a%20b",
    }


def test_calculate_md5_for_string() -> None:
    """A string is UTF-8 encoded and hashed to its MD5 hex digest."""
    service = FileStorageService()

    assert service._calculate_md5("hello") == HELLO_MD5


def test_calculate_md5_for_file(tmp_path: Path) -> None:
    """With is_path=True the file contents are hashed, matching a direct MD5."""
    service = FileStorageService()
    file_path = tmp_path / "payload.bin"
    content = b"some binary content \x00\x01\x02"
    file_path.write_bytes(content)

    expected = hashlib.md5(content).hexdigest()

    assert service._calculate_md5(str(file_path), is_path=True) == expected


def test_is_duplicate_true_on_matching_etag() -> None:
    """When the S3 ETag matches the local content's MD5, the object is a duplicate."""
    service = FileStorageService()
    client = AsyncMock()
    client.head_object.return_value = {"ETag": f'"{HELLO_MD5}"'}
    _patch_client(service, client)

    result = asyncio.run(service.is_duplicate("raw-news/x", "hello"))

    assert result is True


def test_is_duplicate_false_on_mismatched_etag() -> None:
    """A differing ETag means the content is not a duplicate."""
    service = FileStorageService()
    client = AsyncMock()
    client.head_object.return_value = {"ETag": '"0000000000000000000000000000dead"'}
    _patch_client(service, client)

    result = asyncio.run(service.is_duplicate("raw-news/x", "hello"))

    assert result is False


def test_is_duplicate_false_on_404() -> None:
    """A 404 (object absent) is treated as 'not a duplicate', not an error."""
    service = FileStorageService()
    client = AsyncMock()
    client.head_object.side_effect = _client_error("404")
    _patch_client(service, client)

    result = asyncio.run(service.is_duplicate("raw-news/missing", "hello"))

    assert result is False


def test_is_duplicate_false_on_no_such_key() -> None:
    """A NoSuchKey error is also treated as 'not a duplicate'."""
    service = FileStorageService()
    client = AsyncMock()
    client.head_object.side_effect = _client_error("NoSuchKey")
    _patch_client(service, client)

    result = asyncio.run(service.is_duplicate("raw-news/missing", "hello"))

    assert result is False
