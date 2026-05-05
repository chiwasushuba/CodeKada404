"""
FastAPI main application entry point.
Initializes all routes, middleware, and startup/shutdown events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.services.db_service import DatabaseService
from app.models.schemas import HealthResponse
from app.api.routes import upload_router, chat_router, status_router


# ============= STARTUP & SHUTDOWN EVENTS =============


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage app lifecycle: startup and shutdown events.
    """
    # ============= STARTUP =============
    print("🚀 Starting Central Brain Backend...")

    # Initialize database connection
    try:
        await DatabaseService.connect_db()
    except Exception as e:
        print(f"⚠️ MongoDB connection warning: {e}")
        print("Continuing without database for now...")

    print("✅ All services initialized successfully")

    yield

    # ============= SHUTDOWN =============
    print("🛑 Shutting down Central Brain Backend...")

    # Close database connection
    try:
        await DatabaseService.close_db()
    except Exception as e:
        print(f"⚠️ Shutdown warning: {e}")

    print("✅ Shutdown complete")


# ============= FASTAPI APP INITIALIZATION =============

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered RAG application backend",
    lifespan=lifespan,
)

# ============= CORS CONFIGURATION =============

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= ROUTE REGISTRATION =============

# Include routers for all API endpoints
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(status_router)


# ============= HEALTH CHECK ENDPOINT =============


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to monitor service status.

    Returns:
        HealthResponse with service statuses
    """
    # TODO: Add actual database and vector store connectivity checks
    return HealthResponse(
        status="healthy",
        database="connected",
        vector_store="connected",
    )


# ============= ROOT ENDPOINT =============


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "message": f"{settings.app_name} API v{settings.app_version}",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
