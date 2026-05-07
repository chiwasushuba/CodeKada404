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


class UploadedFileItem(BaseModel):
    """Single uploaded file entry returned for the knowledge page."""

    file_name: str = Field(..., description="Uploaded file name")
    r2_path: str = Field(..., description="Object key in Cloudflare R2")
    size: int = Field(..., description="File size in bytes")
    uploaded_at: str = Field(..., description="Timestamp when the file was uploaded")


class UploadedFilesResponse(BaseModel):
    """Response containing all files already uploaded to R2."""

    files: list[UploadedFileItem] = Field(
        default_factory=list, description="Previously uploaded files"
    )
    total_files: int = Field(..., description="Total uploaded file count")
    status: str = Field(default="success", description="Response status")


class DeleteFileResponse(BaseModel):
    """Response after deleting an uploaded file."""

    file_name: str = Field(..., description="Deleted file name")
    r2_path: str = Field(..., description="Deleted R2 object key")
    deleted_vectors: int = Field(
        default=0, description="Number of Pinecone vectors deleted"
    )
    deleted_knowledge_records: int = Field(
        default=0, description="Number of knowledge DB records deleted for this file"
    )
    status: str = Field(default="success", description="Deletion status")


class KnowledgeFileItem(BaseModel):
    """Single knowledge file entry for context verification."""

    id: str = Field(..., description="Unique file ID from MongoDB")
    filename: str = Field(..., description="Uploaded file name")
    r2_path: str = Field(default="", description="Object key in Cloudflare R2")
    ai_context: str = Field(..., description="AI-generated or manually updated context")
    is_verified: bool = Field(
        default=False, description="Whether the context has been verified by a user"
    )


class KnowledgeFilesResponse(BaseModel):
    """Response containing knowledge files for verification."""

    files: list[KnowledgeFileItem] = Field(
        default_factory=list, description="Knowledge files and their context status"
    )
    total_files: int = Field(..., description="Total knowledge file count")
    status: str = Field(default="success", description="Response status")


class VerifyKnowledgeFileResponse(BaseModel):
    """Response after marking a file context as verified."""

    id: str = Field(..., description="Updated file ID")
    is_verified: bool = Field(..., description="Verification status")
    status: str = Field(default="success", description="Response status")


class DeleteKnowledgeFileResponse(BaseModel):
    """Response after deleting a knowledge file context."""

    id: str = Field(..., description="Deleted file ID")
    r2_path: str = Field(default="", description="Associated R2 object key")
    deleted_vectors: int = Field(default=0, description="Number of Pinecone vectors deleted")
    status: str = Field(default="success", description="Response status")


class UpdateKnowledgeContextRequest(BaseModel):
    """Request payload for manual context updates."""

    manual_context: str = Field(..., min_length=1, description="Updated context text")


class UpdateKnowledgeContextResponse(BaseModel):
    """Response after manual context update and re-embedding."""

    id: str = Field(..., description="Updated file ID")
    ai_context: str = Field(..., description="Persisted context text")
    is_verified: bool = Field(..., description="Verification status after update")
    reembedded_chunks: int = Field(..., description="Number of chunks re-embedded in Pinecone")
    status: str = Field(default="success", description="Response status")


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
