"""
Application entry point for Render deployment.
Reads configuration from .env and starts the Uvicorn server.
"""

import uvicorn
import os
from app.core.config import settings

if __name__ == "__main__":
    # 1. Grab Render's dynamic PORT, fallback to your settings.port for local dev
    render_port = int(os.environ.get("PORT", settings.port))
    
    # 2. Force the host to 0.0.0.0 if running in production/Render
    render_host = "0.0.0.0" if os.environ.get("RENDER") else settings.host

    uvicorn.run(
        "app.main:app",
        host=render_host,     # CRITICAL: Forces 0.0.0.0 on Render
        port=render_port,     # CRITICAL: Uses Render's dynamic port
        log_level=settings.log_level,
        reload=settings.reload, 
    )