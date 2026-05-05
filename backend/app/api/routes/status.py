"""
Status update endpoint.
Handles developer status updates and AI-generated summaries.
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from app.models.schemas import StatusUpdate, StatusResponse
from app.services.db_service import DatabaseService, get_db_service
from app.services.llm_service import LLMService, get_llm_service

router = APIRouter(prefix="/api", tags=["status"])


@router.post("/status", response_model=StatusResponse)
async def post_status(
    status: StatusUpdate,
    db_service: DatabaseService = Depends(get_db_service),
    llm_service: LLMService = Depends(get_llm_service),
):
    """
    Accept developer status update and generate AI summary.

    Flow:
    1. Validate and prepare status data
    2. Save raw status update to MongoDB
    3. Generate AI summary using Gemini
    4. Return status ID and summary

    Args:
        status: StatusUpdate with developer name and update text
        db_service: Injected database service
        llm_service: Injected LLM service

    Returns:
        StatusResponse with status ID and AI-generated summary
    """
    try:
        # ============= 1. Prepare Status Data =============
        timestamp = status.timestamp or datetime.utcnow().isoformat()

        status_data = {
            "developer_name": status.developer_name,
            "update_text": status.update_text,
            "timestamp": timestamp,
            "created_at": datetime.utcnow().isoformat(),
        }

        # ============= 2. Save to MongoDB =============
        status_id = await db_service.save_status_update(status_data)

        # ============= 3. Generate Summary with Gemini =============
        # TODO: Implement daily summary aggregation
        # Currently summarizing individual updates
        summary = await llm_service.summarize_text(status.update_text)

        # ============= 4. Return Response =============
        return StatusResponse(
            status_id=status_id,
            summary=summary,
            stored_at=timestamp,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Status update failed: {str(e)}"
        )


@router.get("/status/daily-summary")
async def get_daily_summary(
    db_service: DatabaseService = Depends(get_db_service),
    llm_service: LLMService = Depends(get_llm_service),
):
    """
    Get AI-generated summary of all status updates from today.

    Flow:
    1. Retrieve all status updates from today
    2. Concatenate update texts
    3. Generate consolidated summary via Gemini
    4. Return summary

    Args:
        db_service: Injected database service
        llm_service: Injected LLM service

    Returns:
        Dictionary with date and consolidated summary
    """
    try:
        # ============= 1. Retrieve Today's Status Updates =============
        # TODO: Filter by date range (today only)
        status_updates = await db_service.get_status_updates(limit=50)

        if not status_updates:
            return {
                "date": datetime.utcnow().isoformat(),
                "summary": "No status updates recorded today.",
            }

        # ============= 2. Compile All Updates =============
        combined_text = "\n\n".join(
            [
                f"Developer: {update.get('developer_name')}\n{update.get('update_text')}"
                for update in status_updates
            ]
        )

        # ============= 3. Generate Consolidated Summary =============
        daily_summary = await llm_service.summarize_text(combined_text)

        return {
            "date": datetime.utcnow().isoformat(),
            "summary": daily_summary,
            "update_count": len(status_updates),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get daily summary: {str(e)}"
        )
