"""Pydantic response models for API endpoints."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProgressUpdate(BaseModel):
    """Progress update for WebSocket."""
    task_id: str
    status: TaskStatus
    progress: int = Field(ge=0, le=100)
    total: int = 100
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScrapeStartResponse(BaseModel):
    """Response when starting a scrape task."""
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    message: str = "Scraping task started"
    websocket_url: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123-def456",
                "status": "pending",
                "message": "Scraping task started",
                "websocket_url": "/ws/task/abc123-def456"
            }
        }


class OverallSentiment(BaseModel):
    """Overall sentiment summary."""
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    average_rating: float
    total_reviews_analyzed: int


class SummaryCounts(BaseModel):
    """Summary counts by category."""
    bugs: int = 0
    features: int = 0
    requirements: int = 0
    usability: int = 0
    pain_points: int = 0
    positive: int = 0
    ai_insights: int = 0


class Finding(BaseModel):
    """A single finding from analysis."""
    type: str
    category: str
    title: str
    description: str
    frequency: int
    severity: str
    sample_reviews: List[str]
    recommendation: str
    priority_score: int
    sources: List[str]


class PriorityAction(BaseModel):
    """A priority action recommendation."""
    action: str
    reason: str
    expected_impact: str
    effort_required: str


class SentimentAnalysis(BaseModel):
    """Full sentiment analysis result."""
    overall_sentiment: OverallSentiment
    summary_counts: SummaryCounts
    bugs: List[Finding] = []
    feature_requests: List[Finding] = []
    requirements: List[Finding] = []
    usability_frictions: List[Finding] = []
    pain_points: List[Finding] = []
    positive_reviews: List[Finding] = []
    ai_insights: List[Finding] = []
    priority_actions: List[PriorityAction] = []
    key_insights: List[str] = []


class DataSummary(BaseModel):
    """Summary of data from each source."""
    source: str
    total_items: int
    analyzed_items: int


class TaskResult(BaseModel):
    """Complete task result."""
    task_id: str
    status: TaskStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    sources: List[str] = []
    sentiment_analysis: Optional[SentimentAnalysis] = None
    data_summary: Dict[str, Any] = {}
    processing_mode: str = ""
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskStatusResponse(BaseModel):
    """Response for task status check."""
    task_id: str
    status: TaskStatus
    progress: int = 0
    message: str = ""
    result: Optional[TaskResult] = None
    error: Optional[str] = None


class PrioritizationPlan(BaseModel):
    """Prioritization plan from Gemini."""
    plan_metadata: Dict[str, Any]
    prioritized_categories: List[Dict[str, Any]]
    summary: Dict[str, Any]


class PrioritizationResponse(BaseModel):
    """Response for prioritization request."""
    task_id: str
    plan: Optional[PrioritizationPlan] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    redis_connected: bool


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
