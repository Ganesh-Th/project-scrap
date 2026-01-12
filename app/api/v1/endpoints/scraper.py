"""Scraper API endpoints."""
import uuid
import asyncio

from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends

from app.config import get_settings
from app.logging_config import get_logger
from app.core.redis_store import RedisTaskStore, get_redis_store
from app.core.connection_manager import get_connection_manager
from app.models.requests import (
    GooglePlayRequest,
    AppleStoreRequest,
    RedditRequest,
    GoogleSearchRequest,
    MultiSourceScrapeRequest,
    PrioritizationRequest
)
from app.models.responses import (
    TaskStatus,
    ScrapeStartResponse,
    TaskStatusResponse,
    TaskResult,
    PrioritizationResponse,
    ErrorResponse
)
from app.services.google_play import scrape_google_play_reviews
from app.services.apple_store import scrape_apple_store_reviews
from app.services.reddit import scrape_reddit
from app.services.google_search import scrape_google_search
from app.services.sentiment import analyze_sentiment_with_gemini
from app.services.data_processor import build_gemini_query
from app.services.prioritization import perform_prioritization


logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()


async def _run_scrape_task(
    task_id: str,
    request: MultiSourceScrapeRequest,
    store: RedisTaskStore
) -> None:
    """Background task to run multi-source scraping and sentiment analysis."""
    try:
        await store.update_task_status(
            task_id, 
            TaskStatus.RUNNING, 
            progress=5, 
            message="Starting scrapers..."
        )
        
        tasks_to_run = []
        sources = []
        
        # Google Play Store
        if request.google_play:
            tasks_to_run.append(
                scrape_google_play_reviews(
                    request.google_play.product_id,
                    request.google_play.platform
                )
            )
            sources.append("google_play_store")
        
        # Apple App Store
        if request.apple_store:
            tasks_to_run.append(
                scrape_apple_store_reviews(
                    request.apple_store.product_id,
                    request.apple_store.country,
                    request.apple_store.target_reviews
                )
            )
            sources.append("apple_app_store")
        
        # Reddit
        if request.include_reddit:
            reddit_keyword = request.reddit.keyword if request.reddit else request.product_name
            limit_pages = request.reddit.limit_pages if request.reddit else 2
            tasks_to_run.append(scrape_reddit(reddit_keyword, limit_pages))
            sources.append("reddit")
        
        # Google Search
        if request.include_google_search:
            search_product = request.google_search.product_name if request.google_search else request.product_name
            tasks_to_run.append(scrape_google_search(search_product))
            sources.append("google_search")
        
        if not tasks_to_run:
            await store.set_task_error(task_id, "No sources configured for scraping")
            return
        
        await store.update_task_status(
            task_id,
            TaskStatus.RUNNING,
            progress=10,
            message=f"Scraping {len(tasks_to_run)} sources: {', '.join(sources)}"
        )
        
        # Run all scrapers concurrently
        results = await asyncio.gather(*tasks_to_run, return_exceptions=True)
        
        # Filter valid results
        scrape_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error in scraper {sources[i]}: {result}")
                continue
            if result and len(result) >= 4:
                data = result[-2]
                if data:
                    scrape_results.append(result)
        
        if not scrape_results:
            await store.set_task_error(task_id, "No valid results from any scraper")
            return
        
        await store.update_task_status(
            task_id,
            TaskStatus.RUNNING,
            progress=50,
            message=f"Scraped {len(scrape_results)} sources. Running sentiment analysis..."
        )
        
        # Build combined query
        combined_query, data_summary = build_gemini_query(scrape_results)
        
        if not combined_query:
            await store.set_task_error(task_id, "Failed to build query from scraped data")
            return
        
        await store.update_task_status(
            task_id,
            TaskStatus.RUNNING,
            progress=60,
            message="Analyzing sentiment with Gemini AI..."
        )
        
        # Run sentiment analysis
        sentiment_result = await analyze_sentiment_with_gemini(
            combined_query,
            data_summary,
            scrape_results,
            request.product_name
        )
        
        if sentiment_result.get("error"):
            await store.set_task_error(task_id, sentiment_result["error"])
            return
        
        await store.update_task_status(
            task_id,
            TaskStatus.RUNNING,
            progress=95,
            message="Saving results..."
        )
        
        # Store result
        await store.set_task_result(task_id, sentiment_result)
        
        await store.update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            progress=100,
            message="Analysis complete!"
        )
        
        logger.info(f"Task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}", exc_info=True)
        await store.set_task_error(task_id, str(e))


@router.post(
    "/scrape",
    response_model=ScrapeStartResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Start a multi-source scrape task",
    description="Starts a background task to scrape reviews from multiple sources and perform sentiment analysis"
)
async def start_scrape(
    request: MultiSourceScrapeRequest,
    background_tasks: BackgroundTasks,
    store: RedisTaskStore = Depends(get_redis_store)
):
    """Start a multi-source scraping task."""
    task_id = str(uuid.uuid4())
    
    # Determine sources
    sources = []
    if request.google_play:
        sources.append("google_play_store")
    if request.apple_store:
        sources.append("apple_app_store")
    if request.include_reddit:
        sources.append("reddit")
    if request.include_google_search:
        sources.append("google_search")
    
    if not sources:
        raise HTTPException(
            status_code=400, 
            detail="At least one data source must be configured"
        )
    
    # Create task in Redis
    await store.create_task(task_id, {
        "sources": sources,
        "request": request.model_dump()
    })
    
    # Start background task
    background_tasks.add_task(_run_scrape_task, task_id, request, store)
    
    return ScrapeStartResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message=f"Scraping task started for sources: {', '.join(sources)}",
        websocket_url=f"/ws/task/{task_id}"
    )


@router.get(
    "/task/{task_id}",
    response_model=TaskStatusResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get task status",
    description="Retrieves the current status and result of a scrape task"
)
async def get_task_status(
    task_id: str,
    store: RedisTaskStore = Depends(get_redis_store)
):
    """Get task status and result."""
    task_data = await store.get_task(task_id)
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = TaskStatus(task_data.get("status", "pending"))
    result = None
    
    if status == TaskStatus.COMPLETED and task_data.get("result"):
        result = TaskResult(
            task_id=task_id,
            status=status,
            created_at=task_data.get("created_at"),
            completed_at=task_data.get("completed_at"),
            sources=task_data.get("sources", []),
            sentiment_analysis=task_data["result"].get("sentiment_analysis"),
            data_summary=task_data["result"].get("data_summary", {}),
            processing_mode=task_data["result"].get("processing_mode", "")
        )
    
    return TaskStatusResponse(
        task_id=task_id,
        status=status,
        progress=int(task_data.get("progress", 0)),
        message=task_data.get("message", ""),
        result=result,
        error=task_data.get("error")
    )


@router.post(
    "/prioritize",
    response_model=PrioritizationResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Prioritize tasks from analysis",
    description="Uses Gemini to prioritize findings from a completed scrape task"
)
async def prioritize_tasks(
    request: PrioritizationRequest,
    store: RedisTaskStore = Depends(get_redis_store)
):
    """Prioritize tasks from a completed sentiment analysis."""
    task_data = await store.get_task(request.task_id)
    
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = TaskStatus(task_data.get("status", "pending"))
    
    if status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"Task is not completed. Current status: {status.value}"
        )
    
    result = task_data.get("result")
    if not result:
        raise HTTPException(status_code=400, detail="No result data found for task")
    
    toon_content = result.get("toon_text", "")
    if not toon_content:
        raise HTTPException(
            status_code=400, 
            detail="No TOON data available from sentiment analysis"
        )
    
    plan = await perform_prioritization(
        toon_content,
        request.method,
        request.duration,
        request.budget,
        request.business_goal
    )
    
    if plan.get("error"):
        raise HTTPException(status_code=500, detail=plan["error"])
    
    return PrioritizationResponse(
        task_id=request.task_id,
        plan=plan
    )


@router.websocket("/ws/task/{task_id}")
async def websocket_task_progress(
    websocket: WebSocket,
    task_id: str
):
    """WebSocket endpoint for real-time task progress updates."""
    manager = get_connection_manager()
    
    try:
        await manager.connect(websocket, task_id)
        
        # Keep connection alive until client disconnects or task completes
        while True:
            try:
                # Wait for any client message (ping/pong or close)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                # Client can send "close" to disconnect
                if data == "close":
                    break
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
                    
    except WebSocketDisconnect:
        logger.error(f"WebSocket disconnected for task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
    finally:
        await manager.disconnect(websocket, task_id)


# Single-source endpoints for flexibility
@router.post(
    "/scrape/google-play",
    response_model=ScrapeStartResponse,
    summary="Scrape Google Play Store only"
)
async def scrape_google_play_only(
    request: GooglePlayRequest,
    background_tasks: BackgroundTasks,
    store: RedisTaskStore = Depends(get_redis_store)
):
    """Start a Google Play Store scrape task."""
    multi_request = MultiSourceScrapeRequest(
        product_name=request.product_id,
        google_play=request,
        include_reddit=False,
        include_google_search=False
    )
    return await start_scrape(multi_request, background_tasks, store)


@router.post(
    "/scrape/apple-store",
    response_model=ScrapeStartResponse,
    summary="Scrape Apple App Store only"
)
async def scrape_apple_store_only(
    request: AppleStoreRequest,
    background_tasks: BackgroundTasks,
    store: RedisTaskStore = Depends(get_redis_store)
):
    """Start an Apple App Store scrape task."""
    multi_request = MultiSourceScrapeRequest(
        product_name=request.product_id,
        apple_store=request,
        include_reddit=False,
        include_google_search=False
    )
    return await start_scrape(multi_request, background_tasks, store)


@router.post(
    "/scrape/reddit",
    response_model=ScrapeStartResponse,
    summary="Scrape Reddit only"
)
async def scrape_reddit_only(
    request: RedditRequest,
    background_tasks: BackgroundTasks,
    store: RedisTaskStore = Depends(get_redis_store)
):
    """Start a Reddit scrape task."""
    multi_request = MultiSourceScrapeRequest(
        product_name=request.keyword,
        reddit=request,
        include_reddit=True,
        include_google_search=False
    )
    return await start_scrape(multi_request, background_tasks, store)


@router.post(
    "/scrape/google-search",
    response_model=ScrapeStartResponse,
    summary="Scrape Google Search only"
)
async def scrape_google_search_only(
    request: GoogleSearchRequest,
    background_tasks: BackgroundTasks,
    store: RedisTaskStore = Depends(get_redis_store)
):
    """Start a Google Search scrape task."""
    multi_request = MultiSourceScrapeRequest(
        product_name=request.product_name,
        google_search=request,
        include_reddit=False,
        include_google_search=True
    )
    return await start_scrape(multi_request, background_tasks, store)
