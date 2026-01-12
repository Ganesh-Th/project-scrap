"""FastAPI application initialization."""
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.logging_config import setup_logging, get_logger
from app.core.redis_store import RedisTaskStore
from app.api.v1.endpoints import scraper


# Initialize logging
setup_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events."""
    # Startup
    logger.info("Starting Multi-Source Scraper API...")
    
    try:
        # Initialize Redis connection
        await RedisTaskStore.get_instance()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        logger.warning("Application will start but task persistence will not work")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-Source Scraper API...")
    
    try:
        store = await RedisTaskStore.get_instance()
        await store.disconnect()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Sentiment to Sprint",
        description="""
## Overview
A production-ready FastAPI application for scraping reviews from multiple sources 
and performing AI-powered sentiment analysis using Google Gemini.

## Features
- **Multi-Source Scraping**: Google Play Store, Apple App Store, Reddit, Google Search
- **AI Sentiment Analysis**: Powered by Google Gemini with URL context and social media search
- **Real-time Progress**: WebSocket updates for task monitoring
- **Task Persistence**: Redis-backed task storage with 24-hour TTL
- **Prioritization**: MoSCoW and Lean prioritization frameworks

## Data Sources
| Source | Description |
|--------|-------------|
| Google Play Store | App reviews via SerpAPI |
| Apple App Store | App reviews via SerpAPI |
| Reddit | Posts and comments via web scraping |
| Google Search | Review articles and blog posts |

## Analysis Types
The AI categorizes findings into 7 types:
- **bug**: Technical issues, crashes, errors
- **feature_request**: User-requested enhancements
- **requirement**: Must-have missing features
- **usability_friction**: UX issues
- **pain_point**: General dissatisfaction
- **positive_review**: Praised features
- **ai_insight**: AI-discovered patterns

## Usage
1. Start a scrape task via `POST /api/v1/scrape`
2. Connect to WebSocket at `/ws/task/{task_id}` for real-time updates
3. Retrieve results via `GET /api/v1/task/{task_id}`
4. Optionally prioritize via `POST /api/v1/prioritize`
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # CORS configuration
    origins = [
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", ""),
        "https://*.vercel.app",
    ]
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(
        scraper.router,
        prefix="/api/v1",
        tags=["Scraper"]
    )
    
    @app.get("/", tags=["Health"])
    async def root():
        """Root endpoint with API info."""
        return {
            "name": "Multi-Source Review Scraper API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        redis_connected = False
        
        try:
            store = await RedisTaskStore.get_instance()
            redis_connected = await store.is_connected()
        except Exception as exc:
            logger.warning(f"Health check: failed to verify Redis connectivity: {exc}")
        
        return {
            "status": "healthy" if redis_connected else "degraded",
            "version": "1.0.0",
            "redis_connected": redis_connected
        }
    
    return app


# Create application instance
app = create_app()
