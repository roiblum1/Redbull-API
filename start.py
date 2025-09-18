#!/usr/bin/env python3
"""Startup script for MCE Cluster Generator API."""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    import uvicorn
    from src.config import settings
    
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Server: http://{settings.HOST}:{settings.PORT}")
    print(f"Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )