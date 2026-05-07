"""
Knowledge context verification endpoints.
Handles listing, verifying, and manually correcting AI context for uploaded files.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import (
    KnowledgeFileItem,
    KnowledgeFilesResponse,
    VerifyKnowledgeFileResponse,
    UpdateKnowledgeContextRequest,
    UpdateKnowledgeContextResponse,
)
from app.services.db_service import DatabaseService, get_db_service
from app.services.llm_service import LLMService, get_llm_service
from app.services.vector_service import VectorService, get_vector_service

router = APIRouter(prefix="/api", tags=["knowledge"])


@router.get("/knowledge", response_model=KnowledgeFilesResponse)
async def get_knowledge_files(
    db_service: DatabaseService = Depends(get_db_service),
):
    """Return all uploaded files with AI context and verification state."""
    try:
        records = await db_service.list_knowledge_files()
        files = [
            KnowledgeFileItem(
                id=str(record.get("id", "")),
                filename=record.get("file_name", "Unknown"),
                ai_context=record.get("ai_context", ""),
                is_verified=bool(record.get("is_verified", False)),
            )
            for record in records
        ]

        return KnowledgeFilesResponse(files=files, total_files=len(files), status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load knowledge files: {str(e)}")


@router.patch("/knowledge/{file_id}/verify", response_model=VerifyKnowledgeFileResponse)
async def verify_knowledge_context(
    file_id: str,
    db_service: DatabaseService = Depends(get_db_service),
):
    """Mark a file context as verified by the user."""
    try:
        updated = await db_service.mark_knowledge_file_verified(file_id)
        if not updated:
            raise HTTPException(status_code=404, detail="Knowledge file not found")

        return VerifyKnowledgeFileResponse(
            id=str(updated.get("id", file_id)),
            is_verified=bool(updated.get("is_verified", True)),
            status="success",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify context: {str(e)}")


@router.patch("/knowledge/{file_id}/update-context", response_model=UpdateKnowledgeContextResponse)
async def update_knowledge_context(
    file_id: str,
    payload: UpdateKnowledgeContextRequest,
    db_service: DatabaseService = Depends(get_db_service),
    llm_service: LLMService = Depends(get_llm_service),
    vector_service: VectorService = Depends(get_vector_service),
):
    """
    Update manual context and re-embed into Pinecone.

    Pinecone integration note:
    - This endpoint deletes existing vectors for the file and writes new vectors from manual context.
    - If your production strategy needs partial updates or versioned namespaces, update this flow.
    """
    try:
        existing = await db_service.get_knowledge_file_by_id(file_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Knowledge file not found")

        manual_context = payload.manual_context.strip()
        if not manual_context:
            raise HTTPException(status_code=400, detail="manual_context is required")

        persisted = await db_service.update_knowledge_context(file_id, manual_context)
        if not persisted:
            raise HTTPException(status_code=404, detail="Knowledge file not found")

        r2_path = existing.get("r2_path", "")
        if r2_path:
            # TODO: If needed, scope this delete to a namespace per tenant/user.
            await vector_service.delete_vectors_by_filter({"r2_path": {"$eq": r2_path}})

        chunks = _chunk_text(manual_context)
        vectors_to_upsert = []
        uploaded_at = datetime.utcnow().isoformat()
        file_name = existing.get("file_name", "unknown")

        for chunk_index, chunk_text in enumerate(chunks):
            embeddings = await llm_service.generate_embeddings(
                chunk_text, task_type="retrieval_document"
            )
            vector_id = f"{uploaded_at}_{file_name}_manual_{chunk_index}"
            vectors_to_upsert.append(
                {
                    "id": vector_id,
                    "values": embeddings,
                    "metadata": {
                        "file_name": file_name,
                        "r2_path": r2_path,
                        "file_type": "manual_context",
                        "uploaded_at": uploaded_at,
                        "chunk_index": chunk_index,
                        "chunk_text": chunk_text,
                        "is_manual_context": True,
                    },
                }
            )

        await vector_service.upsert_vectors(vectors_to_upsert)
        # TODO: For production, consider versioned vectors instead of delete+replace.

        return UpdateKnowledgeContextResponse(
            id=str(persisted.get("id", file_id)),
            ai_context=persisted.get("ai_context", manual_context),
            is_verified=bool(persisted.get("is_verified", False)),
            reembedded_chunks=len(vectors_to_upsert),
            status="success",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update context: {str(e)}")


def _chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    """Split context text into overlapping chunks before embedding."""
    cleaned = text.strip()
    if not cleaned:
        return ["[No context provided]"]

    chunks = []
    start = 0
    step = max(1, chunk_size - overlap)

    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks or ["[No context provided]"]
