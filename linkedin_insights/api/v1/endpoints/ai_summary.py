"""
AI Summary endpoints
Optional async endpoints for AI-powered page summaries
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from linkedin_insights.db.base import get_db
from linkedin_insights.schemas.ai_summary import (
    PageStatsRequest,
    AISummaryResponse,
    AISummaryErrorResponse,
)
from linkedin_insights.services.linkedin_page_service import LinkedInPageService
from linkedin_insights.services.ai_summary_service import get_ai_summary_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/pages/{page_id}/summary",
    summary="Get AI summary for a LinkedIn page",
    response_model=AISummaryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": AISummaryErrorResponse, "description": "Page not found"},
        503: {"model": AISummaryErrorResponse, "description": "AI service unavailable"},
    }
)
async def get_page_ai_summary(
    page_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI-powered summary for a LinkedIn page
    
    This endpoint is optional and requires:
    - OpenAI API key set in OPENAI_API_KEY environment variable
    - OpenAI package installed
    
    Returns summary covering:
    - Page type (Enterprise, Startup, Agency, etc.)
    - Audience characteristics
    - Engagement level and patterns
    """
    # Check if AI service is enabled
    ai_service = get_ai_summary_service()
    if not ai_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": True,
                "message": "AI Summary Service is not available. Please set OPENAI_API_KEY environment variable.",
                "service_enabled": False
            }
        )
    
    # Get page service
    page_service = LinkedInPageService(db)
    
    # Generate summary
    summary = await page_service.generate_ai_summary(page_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": True,
                "message": f"Page with page_id '{page_id}' not found or summary generation failed",
                "service_enabled": True
            }
        )
    
    return summary


@router.post(
    "/summary/generate",
    response_model=AISummaryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        503: {"model": AISummaryErrorResponse, "description": "AI service unavailable"},
    }
)
async def generate_summary_from_stats(
    stats: PageStatsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI summary from provided page statistics
    
    This endpoint accepts page statistics and generates a summary
    without requiring the page to exist in the database.
    """
    # Check if AI service is enabled
    ai_service = get_ai_summary_service()
    if not ai_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": True,
                "message": "AI Summary Service is not available. Please set OPENAI_API_KEY environment variable.",
                "service_enabled": False
            }
        )
    
    # Convert request to dict
    stats_dict = stats.model_dump()
    stats_dict['generated_at'] = None  # Will be set by service
    
    # Generate summary
    summary = ai_service.generate_summary(stats_dict)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": True,
                "message": "Failed to generate summary",
                "service_enabled": True
            }
        )
    
    return summary
