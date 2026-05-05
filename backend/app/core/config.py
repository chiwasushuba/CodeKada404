"""
Core configuration module using Pydantic BaseSettings.
Manages all environment variables and application configuration.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Info
    app_name: str = "Central Brain"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    # Server Configuration
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "info"
    reload: bool = True

    # MongoDB
    mongodb_uri: str
    mongodb_database: str = "central_brain"

    # Pinecone
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "central-brain-index"

    # Google Gemini
    google_api_key: str

    # Cloudflare R2 (S3-compatible)
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_s3_bucket_name: str
    aws_s3_endpoint_url: str
    aws_region: str = "us-east-1"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Instantiate settings
settings = Settings()

