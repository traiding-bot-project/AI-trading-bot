"""Module for handling file storage operations using S3-compatible services."""

import hashlib
import logging
from enum import StrEnum
from typing import Literal
from urllib.parse import quote

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_s3 import S3Client

from src.settings import settings

logger = logging.getLogger(__name__)

FILESTORAGE_SERVICE_NAME: Literal["s3"] = "s3"
LOCAL_ENDPOINT_URL = "http://localhost:8333"


class FileStorageFolder(StrEnum):
    """Predefined folders for file storage."""

    RAW_NEWS = "raw-news"
    EXTRACTED_NEWS = "extracted-news"


class FileStorageService:
    """Service for handling file storage operations using S3-compatible services."""

    def __init__(self) -> None:
        """Initialize the file storage service by creating an S3 client and setting the bucket name."""
        self.s3: S3Client = boto3.client(
            FILESTORAGE_SERVICE_NAME,
            endpoint_url=LOCAL_ENDPOINT_URL,
            region_name=settings.filestorage.region_name,
            aws_access_key_id="mock",
            aws_secret_access_key="mock",
        )
        self.bucket_name = settings.filestorage.bucket_name

    def ensure_bucket(self) -> None:
        """Verifies a bucket exists, creating it if it is missing."""
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["404", "NoSuchBucket"]:
                logger.info(f"Bucket '{self.bucket_name}' not found. Creating it...")
                try:
                    self.s3.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Bucket '{self.bucket_name}' successfully created.")
                except ClientError as ce:
                    logger.error(f"Failed to create bucket: {ce}")
                    raise ce
            else:
                logger.error(f"Error checking bucket visibility: {e}")
                raise e

    @staticmethod
    def create_remote_object_name(folder: FileStorageFolder, object_name: str) -> str:
        """Create a remote object name by combining the folder and the object name."""
        return f"{folder}/{object_name}"

    def _handle_file_metadata(self, metadata: dict[str, str]) -> dict[str, str]:
        """Handle file metadata by converting keys to lowercase and replacing spaces with underscores."""
        return {k.lower().replace(" ", "-"): quote(str(v)) for k, v in metadata.items()}

    def _calculate_md5(self, content: str | bytes, is_path: bool = False) -> str:
        """Calculate the MD5 hash of text, bytes, or a local file."""
        md5 = hashlib.md5()
        if is_path:
            with open(content, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5.update(chunk)
        else:
            data = content.encode("utf-8") if isinstance(content, str) else content
            md5.update(data)
        return md5.hexdigest()

    def is_duplicate(self, remote_object_name: str, local_content: str | bytes, is_path: bool = False) -> bool:
        """Check if an object with the same key and identical MD5 content hash already exists in S3."""
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=remote_object_name)

            s3_etag = response.get("ETag", "").strip('"')
            local_md5 = self._calculate_md5(local_content, is_path=is_path)

            return s3_etag == local_md5
        except ClientError as e:
            if e.response["Error"]["Code"] in ["404", "NoSuchKey"]:
                return False
            logger.error(f"Error checking duplication status for {remote_object_name}: {e}")
            return False

    def upload_file(
        self, local_file_path: str, remote_object_name: str, metadata: dict[str, str] | None = None
    ) -> None:
        """Upload a file from a local path to the object storage with optional metadata."""
        try:
            if self.is_duplicate(remote_object_name, local_file_path, is_path=True):
                logger.info(f"Skipping upload: File {remote_object_name} already exists with identical content.")
                return

            extra_args = {}
            if metadata:
                extra_args["Metadata"] = self._handle_file_metadata(metadata)
            self.s3.upload_file(
                Filename=local_file_path, Key=remote_object_name, Bucket=self.bucket_name, ExtraArgs=extra_args
            )
            logger.info(f"File {local_file_path} uploaded to {remote_object_name}")
        except Exception as e:
            logger.error(f"Error uploading file: {e}")

    def download_file(self, local_file_path: str, remote_object_name: str) -> None:
        """Download a file from the object storage to a local path."""
        try:
            self.s3.download_file(Filename=local_file_path, Key=remote_object_name, Bucket=self.bucket_name)
            logger.info(f"File {remote_object_name} downloaded to {local_file_path}")
        except Exception as e:
            logger.error(f"Error downloading file: {e}")

    def upload_text(self, text_content: str, remote_object_name: str, metadata: dict[str, str] | None = None) -> None:
        """Upload text content as a file to the object storage with optional metadata."""
        try:
            if self.is_duplicate(remote_object_name, text_content):
                logger.info(f"Skipping upload: Text for {remote_object_name} already exists with identical content.")
                return

            cleaned_metadata = self._handle_file_metadata(metadata) if metadata else {}
            self.s3.put_object(
                Body=text_content,
                Key=remote_object_name,
                Bucket=self.bucket_name,
                Metadata=cleaned_metadata,
                ContentType="text/plain",
            )
            logger.info(f"Text content uploaded to {remote_object_name}")
        except Exception as e:
            logger.error(f"Error uploading text content: {e}")

    def download_text(self, remote_object_name: str) -> str:
        """Download text content from the object storage."""
        try:
            response = self.s3.get_object(Key=remote_object_name, Bucket=self.bucket_name)
            text_content = response["Body"].read().decode("utf-8")
            logger.info(f"Text content downloaded from {remote_object_name}")
            return text_content
        except Exception as e:
            logger.error(f"Error downloading text content: {e}")
            return ""

    def get_file_metadata(self, remote_object_name: str) -> dict[str, str]:
        """Get metadata of a file stored in the object storage."""
        try:
            response = self.s3.head_object(Key=remote_object_name, Bucket=self.bucket_name)
            metadata = response.get("Metadata", {})
            logger.info(f"Metadata retrieved for {remote_object_name}")
            return metadata
        except Exception as e:
            logger.error(f"Error retrieving metadata: {e}")
            return {}
