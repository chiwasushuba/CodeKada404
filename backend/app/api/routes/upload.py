"""
File upload endpoint.
Handles PDF/TXT file uploads to R2, text extraction, and vector generation.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pathlib import Path
import tempfile
from datetime import datetime
import zipfile
from xml.etree import ElementTree as ET

from charset_normalizer import from_bytes
from pypdf import PdfReader

from app.models.schemas import (
    UploadResponse,
    UploadBatchResponse,
    DeleteFileResponse,
    UploadedFileItem,
    UploadedFilesResponse,
)
from app.services.storage_service import StorageService, get_storage_service
from app.services.llm_service import LLMService, get_llm_service
from app.services.vector_service import VectorService, get_vector_service
from app.services.db_service import DatabaseService, get_db_service

router = APIRouter(prefix="/api", tags=["upload"])


@router.get("/upload/files", response_model=UploadedFilesResponse)
async def list_uploaded_files(
    storage_service: StorageService = Depends(get_storage_service),
):
    """List files already uploaded to R2 for the knowledge page."""
    try:
        objects = await storage_service.list_files(prefix="uploads/")
        files = []

        for obj in sorted(objects, key=lambda item: item.get("modified", ""), reverse=True):
            key = obj.get("key", "")
            file_name = _display_file_name_from_key(key)
            files.append(
                UploadedFileItem(
                    file_name=file_name,
                    r2_path=key,
                    size=int(obj.get("size", 0)),
                    uploaded_at=obj.get("modified", ""),
                )
            )

        return UploadedFilesResponse(files=files, total_files=len(files), status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list uploaded files: {str(e)}")


@router.delete("/upload/files", response_model=DeleteFileResponse)
async def delete_uploaded_file(
    r2_path: str,
    storage_service: StorageService = Depends(get_storage_service),
    vector_service: VectorService = Depends(get_vector_service),
):
    """Delete a single uploaded file and its indexed vectors."""
    try:
        file_name = _display_file_name_from_key(r2_path)

        await storage_service.delete_file(r2_path)
        vector_delete_result = await vector_service.delete_vectors_by_filter(
            {"r2_path": {"$eq": r2_path}}
        )

        deleted_vectors = 0
        if isinstance(vector_delete_result, dict):
            deleted_vectors = int(vector_delete_result.get("deleted_count", 0))

        return DeleteFileResponse(
            file_name=file_name,
            r2_path=r2_path,
            deleted_vectors=deleted_vectors,
            status="success",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.post("/upload", response_model=UploadBatchResponse)
async def upload_file(
    files: list[UploadFile] = File(...),
    storage_service: StorageService = Depends(get_storage_service),
    llm_service: LLMService = Depends(get_llm_service),
    vector_service: VectorService = Depends(get_vector_service),
    db_service: DatabaseService = Depends(get_db_service),
):
    """
    Upload one or more files (PDF, DOCX, MD, TXT), extract text, generate embeddings, and store vectors.

    Flow:
    1. Save file to temporary location
    2. Upload to Cloudflare R2
    3. Extract text from file
    4. Generate embeddings using Gemini API
    5. Store vectors in Pinecone
    6. Save document metadata to MongoDB

    Args:
        files: Files to upload (PDF, DOCX, MD, or TXT)
        storage_service: Injected storage service
        llm_service: Injected LLM service
        vector_service: Injected vector service
        db_service: Injected database service

    Returns:
        UploadBatchResponse with per-file details and vector counts
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="At least one file is required.")

        uploaded_files = []
        allowed_extensions = {".pdf", ".docx", ".md", ".txt"}

        # ============= 1. Validate Files =============
        for file in files:
            file_ext = Path(file.filename).suffix.lower()

            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Only PDF, DOCX, MD, and TXT files are allowed. Received: {file_ext}",
                )

        # ============= 2. Process Each File =============
        for file in files:
            file_ext = Path(file.filename).suffix.lower()

            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name

            try:
                file_size = len(content)

                # ============= 3. Upload to R2 =============
                r2_key = f"uploads/{datetime.utcnow().isoformat()}_{file.filename}"
                await storage_service.upload_file(temp_path, r2_key)

                # ============= 4. Extract Text from File =============
                text_content = await _extract_text(temp_path, file_ext)

                # ============= 5. Generate Chunk Embeddings =============
                chunks = _chunk_text(text_content)
                vectors_to_upsert = []
                uploaded_at = datetime.utcnow().isoformat()

                for chunk_index, chunk_text in enumerate(chunks):
                    embeddings = await llm_service.generate_embeddings(
                        chunk_text, task_type="retrieval_document"
                    )
                    vector_id = (
                        f"{datetime.utcnow().isoformat()}_{file.filename}_{chunk_index}"
                    )
                    vectors_to_upsert.append(
                        {
                            "id": vector_id,
                            "values": embeddings,
                            "metadata": {
                                "file_name": file.filename,
                                "r2_path": r2_key,
                                "file_type": file_ext,
                                "uploaded_at": uploaded_at,
                                "chunk_index": chunk_index,
                                "chunk_text": chunk_text,
                            },
                        }
                    )

                # ============= 6. Store Vectors in Pinecone =============
                await vector_service.upsert_vectors(vectors_to_upsert)

                # ============= 7. Save Metadata to MongoDB =============
                document_metadata = {
                    "file_name": file.filename,
                    "file_size": file_size,
                    "r2_path": r2_key,
                    "vector_count": len(vectors_to_upsert),
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "text_preview": text_content[:500],  # Store first 500 chars
                }

                await db_service.save_document_metadata(document_metadata)

                uploaded_files.append(
                    UploadResponse(
                        file_name=file.filename,
                        file_size=file_size,
                        r2_path=r2_key,
                        vector_count=len(vectors_to_upsert),
                        status="success",
                    )
                )
            finally:
                Path(temp_path).unlink(missing_ok=True)

        return UploadBatchResponse(
            files=uploaded_files,
            total_files=len(uploaded_files),
            status="success",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


async def _extract_text(file_path: str, file_ext: str) -> str:
    """
    Extract text from PDF, DOCX, MD, or TXT file.

    Args:
        file_path: Path to the file
        file_ext: File extension (.pdf or .txt)

    Returns:
        Extracted text content

    TODO: Implement proper PDF text extraction using PyPDF2 or similar
    """
    try:
        if file_ext in {".txt", ".md"}:
            with open(file_path, "rb") as f:
                raw_bytes = f.read()

            for encoding in ("utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "cp1252"):
                try:
                    return raw_bytes.decode(encoding)
                except UnicodeDecodeError:
                    continue

            detected = from_bytes(raw_bytes).best()
            if detected is not None:
                return str(detected)

            return raw_bytes.decode("utf-8", errors="replace")
        elif file_ext == ".docx":
            return _extract_docx_text(file_path)
        elif file_ext == ".pdf":
            reader = PdfReader(file_path)
            pages = []
            for page in reader.pages:
                extracted_text = page.extract_text() or ""
                if extracted_text.strip():
                    pages.append(extracted_text)
            return "\n".join(pages)
    except Exception as e:
        raise Exception(f"Error extracting text: {str(e)}")


def _extract_docx_text(file_path: str) -> str:
    """Extract paragraph text from a DOCX file using the Open XML document body."""
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    with zipfile.ZipFile(file_path) as docx_archive:
        document_xml = docx_archive.read("word/document.xml")

    root = ET.fromstring(document_xml)
    paragraphs = []

    for paragraph in root.findall(".//w:p", namespace):
        text_parts = [node.text for node in paragraph.findall(".//w:t", namespace) if node.text]
        paragraph_text = "".join(text_parts).strip()
        if paragraph_text:
            paragraphs.append(paragraph_text)

    return "\n".join(paragraphs)


def _chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks for better retrieval accuracy."""
    cleaned = text.strip()
    if not cleaned:
        return ["[No extractable text content]"]

    chunks = []
    start = 0
    step = max(1, chunk_size - overlap)

    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks or ["[No extractable text content]"]


def _display_file_name_from_key(r2_path: str) -> str:
    """Convert an uploaded R2 object key back to the original file name for display."""
    if not r2_path:
        return "Unknown"

    key = r2_path.split("/")[-1]
    _, separator, original_name = key.partition("_")
    return original_name if separator and original_name else key
