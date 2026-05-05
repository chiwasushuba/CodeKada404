"""
API routes package for Central Brain application.
Exports routers for all endpoints.
"""

from app.api.routes.upload import router as upload_router
from app.api.routes.chat import router as chat_router
from app.api.routes.status import router as status_router

__all__ = ["upload_router", "chat_router", "status_router"]
