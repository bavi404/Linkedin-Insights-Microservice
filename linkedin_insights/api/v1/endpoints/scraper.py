"""
Scraper endpoints
Endpoints for LinkedIn profile scraping
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from linkedin_insights.db.base import get_db
from linkedin_insights.schemas.scraper import ScrapeRequest, ScrapeResponse
from linkedin_insights.services.scraper_service import ScraperService

router = APIRouter()


@router.post("/scrape", response_model=ScrapeResponse, status_code=status.HTTP_202_ACCEPTED)
def scrape_profile(
    request: ScrapeRequest,
    db: Session = Depends(get_db)
):
    """Scrape LinkedIn profile and create insight"""
    service = ScraperService(db)
    try:
        result = service.scrape_profile(request)
        return ScrapeResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}"
        )

