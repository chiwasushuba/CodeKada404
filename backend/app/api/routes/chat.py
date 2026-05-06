"""
Chat endpoint.
Handles user questions, context retrieval, and AI answer generation.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_service import LLMService, get_llm_service
from app.services.vector_service import VectorService, get_vector_service

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service),
    vector_service: VectorService = Depends(get_vector_service),
):
    """
    Process user question and generate AI answer using RAG.

    Flow:
    1. Generate embedding for user question using Gemini
    2. Search Pinecone for relevant context vectors
    3. Retrieve full context from vector metadata
    4. Send question + context to Gemini for answer generation
    5. Return answer with source references

    Args:
        request: ChatRequest with user question and context limit
        llm_service: Injected LLM service
        vector_service: Injected vector service

    Returns:
        ChatResponse with AI answer and sources
    """
    try:
        # ============= 1. Generate Embedding for Question =============
        question_embedding = await llm_service.generate_embeddings(
            request.question, task_type="retrieval_query"
        )

        # ============= 2. Search Pinecone for Context =============
        search_results = await vector_service.query_vectors(
            query_vector=question_embedding, top_k=request.context_limit
        )

        if not search_results:
            return ChatResponse(
                answer="No relevant context found in knowledge base.",
                sources=[],
                confidence=0.0,
            )

        # ============= 3. Compile Context from Results =============
        context_parts = []
        sources = []

        for result in search_results:
            metadata = result.get("metadata", {})
            file_name = metadata.get("file_name", "Unknown")
            chunk_index = metadata.get("chunk_index", "n/a")
            chunk_text = metadata.get("chunk_text") or metadata.get("text_preview")
            sources.append(file_name)

            if chunk_text:
                context_parts.append(
                    f"Source: {file_name} (chunk {chunk_index})\nContent: {chunk_text}"
                )
            else:
                context_parts.append(
                    f"Source: {file_name} (chunk {chunk_index})\nContent: {str(metadata)}"
                )

        context = "\n---\n".join(context_parts)

        # ============= 4. Generate Answer with Gemini =============
        answer = await llm_service.generate_answer(
            question=request.question,
            context=context,
            system_prompt="You are a helpful AI assistant specializing in answering questions based on provided context. Always cite your sources.",
        )

        # ============= 5. Calculate Confidence Score =============
        # Simple confidence based on similarity score of best match
        confidence = search_results[0].get("score", 0.5) if search_results else 0.0

        return ChatResponse(
            answer=answer,
            sources=list(set(sources)),  # Remove duplicates
            confidence=min(confidence, 1.0),  # Ensure between 0-1
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
