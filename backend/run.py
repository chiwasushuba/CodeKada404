"""
Application entry point for Render deployment.
Reads configuration from .env and starts the Uvicorn server.
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=settings.reload,
    )
