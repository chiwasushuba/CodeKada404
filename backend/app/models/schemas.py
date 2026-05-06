"""
Pydantic schemas for request/response validation.
Defines all data models used across the API.
"""

from typing import Optional
from pydantic import BaseModel, Field


# ============= UPLOAD ENDPOINT =============


class UploadResponse(BaseModel):
    """Response from file upload endpoint."""

    file_name: str = Field(..., description="Name of the uploaded file")
    file_size: int = Field(..., description="Size of the file in bytes")
    r2_path: str = Field(..., description="Path to the file in Cloudflare R2")
    vector_count: int = Field(..., description="Number of vectors generated and stored")
    status: str = Field(default="success", description="Upload status")


class UploadBatchResponse(BaseModel):
    """Response from a batch file upload request."""

    files: list[UploadResponse] = Field(
        default_factory=list, description="Per-file upload results"
    )
    total_files: int = Field(..., description="Total number of uploaded files")
    status: str = Field(default="success", description="Batch upload status")


# ============= CHAT ENDPOINT =============


class ChatRequest(BaseModel):
    """Request for the chat endpoint."""

    question: str = Field(..., description="User question to ask the AI")
    context_limit: int = Field(
        default=5, description="Maximum number of context documents to retrieve"
    )


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    answer: str = Field(..., description="AI-generated answer")
    sources: list[str] = Field(
        default_factory=list, description="List of source documents used"
    )
    confidence: float = Field(
        default=0.5, description="Confidence score of the answer (0-1)"
    )


# ============= STATUS ENDPOINT =============


class StatusUpdate(BaseModel):
    """Request for status update endpoint."""

    developer_name: str = Field(..., description="Name of the developer")
    update_text: str = Field(..., description="Raw status update text")
    timestamp: Optional[str] = Field(
        default=None, description="Optional timestamp (defaults to server time)"
    )


class StatusResponse(BaseModel):
    """Response from status endpoint."""

    status_id: str = Field(..., description="Unique ID of the stored status")
    summary: str = Field(..., description="AI-generated summary of the status")
    stored_at: str = Field(..., description="Timestamp when status was stored")


# ============= HEALTH CHECK =============


class HealthResponse(BaseModel):
    """Response from health check endpoint."""

    status: str = Field(default="healthy", description="Service health status")
    database: str = Field(default="unknown", description="Database connection status")
    vector_store: str = Field(default="unknown", description="Vector store status")
