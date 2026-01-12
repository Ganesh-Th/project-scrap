"""Pydantic request models for API endpoints."""
from typing import Optional
from pydantic import BaseModel, Field


class GooglePlayRequest(BaseModel):
    """Google Play Store scrape request."""
    product_id: str = Field(..., description="Google Play Store product ID (e.g., com.google.android.youtube)")
    platform: str = Field(default="phone", description="Platform type: phone, tablet, chromebook")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "com.google.android.youtube",
                "platform": "phone"
            }
        }


class AppleStoreRequest(BaseModel):
    """Apple App Store scrape request."""
    product_id: str = Field(..., description="Apple App Store product ID (e.g., 544007664)")
    country: str = Field(default="us", description="Country code or name (e.g., us, uk, Germany)")
    target_reviews: int = Field(default=199, ge=1, le=500, description="Number of reviews to fetch")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "544007664",
                "country": "us",
                "target_reviews": 199
            }
        }


class RedditRequest(BaseModel):
    """Reddit scrape request."""
    keyword: str = Field(..., min_length=1, description="Keyword to search (will append ' Review')")
    limit_pages: int = Field(default=2, ge=1, le=50, description="Maximum pages to scrape")
    
    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "YouTube",
                "limit_pages": 2
            }
        }


class GoogleSearchRequest(BaseModel):
    """Google Search scrape request."""
    product_name: str = Field(..., min_length=1, description="Product name to search for reviews")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "YouTube"
            }
        }


class MultiSourceScrapeRequest(BaseModel):
    """Combined multi-source scrape request."""
    product_name: str = Field(..., min_length=1, description="Product name (used for Reddit and Google Search)")
    google_play: Optional[GooglePlayRequest] = Field(None, description="Google Play Store configuration")
    apple_store: Optional[AppleStoreRequest] = Field(None, description="Apple App Store configuration")
    reddit: Optional[RedditRequest] = Field(None, description="Reddit configuration (uses product_name if not specified)")
    google_search: Optional[GoogleSearchRequest] = Field(None, description="Google Search configuration (uses product_name if not specified)")
    include_reddit: bool = Field(default=True, description="Include Reddit scraping")
    include_google_search: bool = Field(default=True, description="Include Google Search scraping")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "YouTube",
                "google_play": {
                    "product_id": "com.google.android.youtube",
                    "platform": "phone"
                },
                "apple_store": {
                    "product_id": "544007664",
                    "country": "us"
                },
                "include_reddit": True,
                "include_google_search": True
            }
        }


class PrioritizationRequest(BaseModel):
    """Task prioritization request."""
    task_id: str = Field(..., description="Task ID from a completed scrape")
    method: str = Field(default="MoSCoW", description="Prioritization framework: MoSCoW or Lean")
    duration: int = Field(default=14, ge=1, le=90, description="Sprint duration in days")
    budget: int = Field(default=160, ge=1, description="Developer hours budget")
    business_goal: str = Field(..., min_length=1, description="Current business goal")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123",
                "method": "MoSCoW",
                "duration": 14,
                "budget": 160,
                "business_goal": "Improve user retention"
            }
        }
