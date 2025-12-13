"""
AI Summary schemas
Pydantic schemas for AI-generated page summaries
"""
from typing import Optional
from pydantic import Field

from linkedin_insights.schemas.base import BaseSchema


class PageStatsRequest(BaseSchema):
    """Schema for page statistics used to generate AI summary"""
    name: str = Field(..., description="Page name")
    industry: Optional[str] = Field(None, description="Industry")
    total_followers: Optional[int] = Field(None, ge=0, description="Total number of followers")
    head_count: Optional[int] = Field(None, ge=0, description="Company head count")
    description: Optional[str] = Field(None, description="Page description")
    total_posts: Optional[int] = Field(None, ge=0, description="Total number of posts")
    avg_likes: Optional[float] = Field(None, ge=0, description="Average likes per post")
    avg_comments: Optional[float] = Field(None, ge=0, description="Average comments per post")
    engagement_rate: Optional[float] = Field(None, ge=0, le=100, description="Engagement rate percentage")


class AISummaryResponse(BaseSchema):
    """Schema for AI-generated summary response"""
    summary: str = Field(..., description="Generated summary text")
    page_type: Optional[str] = Field(None, description="Extracted page type (Enterprise, Startup, Agency, etc.)")
    audience: Optional[str] = Field(None, description="Audience characteristics (Large, Growing, Niche, etc.)")
    engagement: Optional[str] = Field(None, description="Engagement level (High, Moderate, Low)")
    generated_at: Optional[str] = Field(None, description="Timestamp when summary was generated")


class AISummaryErrorResponse(BaseSchema):
    """Schema for AI summary error response"""
    error: bool = Field(True, description="Indicates an error occurred")
    message: str = Field(..., description="Error message")
    service_enabled: bool = Field(..., description="Whether AI service is enabled")

