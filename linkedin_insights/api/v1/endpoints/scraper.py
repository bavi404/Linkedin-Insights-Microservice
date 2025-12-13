"""
Scraper endpoints
Async endpoints for LinkedIn profile scraping
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from linkedin_insights.db.base import get_db
from linkedin_insights.schemas.scraper import ScrapeRequest, ScrapeResponse
from linkedin_insights.services.scraper_service import ScraperService

router = APIRouter()


@router.post("/scrape", response_model=ScrapeResponse, status_code=status.HTTP_202_ACCEPTED)
async def scrape_profile(
    request: ScrapeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Scrape LinkedIn profile and create insight"""
    service = ScraperService()
    try:
        result = await service.scrape_linkedin_page(str(request.profile_url))
        return ScrapeResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}"
        )
