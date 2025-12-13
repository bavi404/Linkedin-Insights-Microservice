"""
Scraper schemas
Pydantic schemas for scraper operations
"""
from typing import Optional
from pydantic import Field, HttpUrl

from linkedin_insights.schemas.base import BaseSchema, TimestampSchema


class ScrapeRequest(BaseSchema):
    """Schema for scrape request"""
    profile_url: HttpUrl = Field(..., description="LinkedIn profile URL to scrape")


class ScrapeResponse(BaseSchema):
    """Schema for scrape response"""
    insight_id: int
    status: str
    message: str


class ScraperRunResponse(TimestampSchema):
    """Schema for scraper run response"""
    id: int
    insight_id: int
    status: str
    error_message: Optional[str] = None
    execution_time: Optional[str] = None

