"""
File upload endpoint.
Handles PDF/TXT file uploads to R2, text extraction, and vector generation.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pathlib import Path
import tempfile
from datetime import datetime

from app.models.schemas import UploadResponse
from app.services.storage_service import StorageService, get_storage_service
from app.services.llm_service import LLMService, get_llm_service
from app.services.vector_service import VectorService, get_vector_service
from app.services.db_service import DatabaseService, get_db_service

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    storage_service: StorageService = Depends(get_storage_service),
    llm_service: LLMService = Depends(get_llm_service),
    vector_service: VectorService = Depends(get_vector_service),
    db_service: DatabaseService = Depends(get_db_service),
):
    """
    Upload a file (PDF/TXT), extract text, generate embeddings, and store vectors.

    Flow:
    1. Save file to temporary location
    2. Upload to Cloudflare R2
    3. Extract text from file
    4. Generate embeddings using Gemini API
    5. Store vectors in Pinecone
    6. Save document metadata to MongoDB

    Args:
        file: File to upload (PDF or TXT)
        storage_service: Injected storage service
        llm_service: Injected LLM service
        vector_service: Injected vector service
        db_service: Injected database service

    Returns:
        UploadResponse with file details and vector count
    """
    try:
        # ============= 1. Validate File =============
        allowed_extensions = {".pdf", ".txt"}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF and TXT files are allowed. Received: {file_ext}",
            )

        # ============= 2. Save File Temporarily =============
        with tempfile.NamedTemporaryFile(
            suffix=file_ext, delete=False
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        file_size = len(content)

        # ============= 3. Upload to R2 =============
        r2_key = f"uploads/{datetime.utcnow().isoformat()}_{file.filename}"
        upload_result = await storage_service.upload_file(temp_path, r2_key)

        # ============= 4. Extract Text from File =============
        text_content = await _extract_text(temp_path, file_ext)

        # ============= 5. Generate Embeddings =============
        # TODO: Implement chunking for large documents
        embeddings = await llm_service.generate_embeddings(text_content)

        # ============= 6. Store Vectors in Pinecone =============
        vector_id = f"{datetime.utcnow().isoformat()}_{file.filename}"
        vectors_to_upsert = [
            {
                "id": vector_id,
                "values": embeddings,
                "metadata": {
                    "file_name": file.filename,
                    "r2_path": r2_key,
                    "file_type": file_ext,
                    "uploaded_at": datetime.utcnow().isoformat(),
                },
            }
        ]

        await vector_service.upsert_vectors(vectors_to_upsert)

        # ============= 7. Save Metadata to MongoDB =============
        document_metadata = {
            "file_name": file.filename,
            "file_size": file_size,
            "r2_path": r2_key,
            "vector_id": vector_id,
            "uploaded_at": datetime.utcnow().isoformat(),
            "text_preview": text_content[:500],  # Store first 500 chars
        }

        doc_id = await db_service.save_document_metadata(document_metadata)

        # ============= 8. Cleanup =============
        Path(temp_path).unlink()

        return UploadResponse(
            file_name=file.filename,
            file_size=file_size,
            r2_path=r2_key,
            vector_count=1,  # Currently storing as single vector; adjust if chunking
            status="success",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


async def _extract_text(file_path: str, file_ext: str) -> str:
    """
    Extract text from PDF or TXT file.

    Args:
        file_path: Path to the file
        file_ext: File extension (.pdf or .txt)

    Returns:
        Extracted text content

    TODO: Implement proper PDF text extraction using PyPDF2 or similar
    """
    try:
        if file_ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif file_ext == ".pdf":
            # TODO: Implement PDF extraction
            # from PyPDF2 import PdfReader
            # pdf = PdfReader(file_path)
            # text = ""
            # for page in pdf.pages:
            #     text += page.extract_text()
            # return text
            return "[PDF extraction not yet implemented]"
    except Exception as e:
        raise Exception(f"Error extracting text: {str(e)}")
