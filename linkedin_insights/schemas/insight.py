"""
Insight schemas
Pydantic schemas for insight request/response
"""
from typing import Optional, Dict, Any
from pydantic import Field, HttpUrl
from pydantic import ConfigDict

from linkedin_insights.schemas.base import BaseSchema, TimestampSchema


class InsightBase(BaseSchema):
    """Base insight schema"""
    profile_url: HttpUrl = Field(..., description="LinkedIn profile URL")
    profile_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    experience: Optional[Dict[str, Any]] = None
    education: Optional[Dict[str, Any]] = None
    skills: Optional[Dict[str, Any]] = None


class InsightCreate(InsightBase):
    """Schema for creating insight"""
    pass


class InsightUpdate(BaseSchema):
    """Schema for updating insight"""
    profile_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    experience: Optional[Dict[str, Any]] = None
    education: Optional[Dict[str, Any]] = None
    skills: Optional[Dict[str, Any]] = None


class InsightResponse(InsightBase, TimestampSchema):
    """Schema for insight response"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class InsightListResponse(BaseSchema):
    """Schema for paginated insight list"""
    items: list[InsightResponse]
    total: int
    page: int
    page_size: int

