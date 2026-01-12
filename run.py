#!/usr/bin/env python
"""Entry point for running the FastAPI application."""
import uvicorn

from app.config import get_settings


def main():
    """Run the FastAPI application with Uvicorn."""
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )


if __name__ == "__main__":
    main()
