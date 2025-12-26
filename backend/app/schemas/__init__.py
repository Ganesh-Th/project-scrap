from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.models import JobState

# Job schemas
class JobCreate(BaseModel):
    app_name: str
    app_id: str

class JobResponse(BaseModel):
    id: int
    app_name: str
    app_id: str
    state: JobState
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

# Review schemas
class ReviewResponse(BaseModel):
    id: int
    author: Optional[str]
    rating: Optional[float]
    content: Optional[str]
    date: Optional[datetime]
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    is_bug: float
    is_feature: float
    is_usability: float
    is_requirement: float
    is_praise: float
    cluster_id: Optional[int]
    
    class Config:
        from_attributes = True

# Theme schemas
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    reach: int
    impact: int
    confidence: int
    effort: int
    rice_score: float
    confirmed: int
    
    class Config:
        from_attributes = True

class ThemeResponse(BaseModel):
    id: int
    cluster_id: int
    title: str
    description: str
    review_count: int
    avg_sentiment: float
    tasks: List[TaskResponse] = []
    
    class Config:
        from_attributes = True

# Task update
class TaskUpdate(BaseModel):
    reach: Optional[int] = None
    impact: Optional[int] = None
    confidence: Optional[int] = None
    effort: Optional[int] = None
    confirmed: Optional[int] = None

# Complete job results
class JobResults(BaseModel):
    job: JobResponse
    reviews: List[ReviewResponse]
    themes: List[ThemeResponse]
