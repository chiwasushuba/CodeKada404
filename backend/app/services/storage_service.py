"""
Cloudflare R2 storage service using Boto3.
Handles file uploads, downloads, and management in R2 bucket.
"""

import boto3
from datetime import datetime
from app.core.config import settings


class StorageService:
    """
    Service for managing file storage with Cloudflare R2.
    Uses Boto3 S3-compatible API.
    """

    def __init__(self):
        """Initialize S3 client for Cloudflare R2."""
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.aws_s3_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.bucket_name = settings.aws_s3_bucket_name

    async def upload_file(
        self, file_path: str, object_key: str, metadata: dict = None
    ) -> dict:
        """
        Upload a file to Cloudflare R2.

        Args:
            file_path: Local path to the file
            object_key: Key/path in R2 bucket (e.g., "uploads/document.pdf")
            metadata: Optional metadata to attach to the file

        Returns:
            Dictionary with upload details
        """
        try:
            # Prepare metadata for the upload
            extra_args = {"ContentType": self._get_content_type(file_path)}
            if metadata:
                extra_args["Metadata"] = metadata

            # Upload file
            self.s3_client.upload_file(
                file_path, self.bucket_name, object_key, ExtraArgs=extra_args
            )

            print(f"✓ File uploaded to R2: {object_key}")
            return {
                "bucket": self.bucket_name,
                "key": object_key,
                "url": f"{settings.aws_s3_endpoint_url}/{self.bucket_name}/{object_key}",
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            print(f"✗ Error uploading file to R2: {e}")
            raise

    async def download_file(self, object_key: str, output_path: str) -> str:
        """
        Download a file from Cloudflare R2.

        Args:
            object_key: Key/path in R2 bucket
            output_path: Local path where to save the file

        Returns:
            Path to the downloaded file
        """
        try:
            self.s3_client.download_file(self.bucket_name, object_key, output_path)
            print(f"✓ File downloaded from R2: {object_key}")
            return output_path
        except Exception as e:
            print(f"✗ Error downloading file from R2: {e}")
            raise

    async def delete_file(self, object_key: str) -> bool:
        """
        Delete a file from Cloudflare R2.

        Args:
            object_key: Key/path in R2 bucket

        Returns:
            True if successful
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            print(f"✓ File deleted from R2: {object_key}")
            return True
        except Exception as e:
            print(f"✗ Error deleting file from R2: {e}")
            raise

    async def list_files(self, prefix: str = "") -> list[dict]:
        """
        List files in R2 bucket with optional prefix.

        Args:
            prefix: Prefix to filter objects (e.g., "uploads/")

        Returns:
            List of file objects
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )
            objects = response.get("Contents", [])
            return [
                {
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "modified": obj["LastModified"].isoformat(),
                }
                for obj in objects
            ]
        except Exception as e:
            print(f"✗ Error listing files from R2: {e}")
            raise

    @staticmethod
    def _get_content_type(file_path: str) -> str:
        """
        Determine content type based on file extension.

        Args:
            file_path: Path to the file

        Returns:
            Content-Type string
        """
        content_types = {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".json": "application/json",
            ".csv": "text/csv",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        ext = file_path[file_path.rfind(".") :].lower()
        return content_types.get(ext, "application/octet-stream")


# Dependency injection function
async def get_storage_service() -> StorageService:
    """Dependency injection for storage service."""
    return StorageService()
