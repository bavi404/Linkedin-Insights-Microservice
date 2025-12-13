"""
Scraper service
Business logic for LinkedIn scraping operations
"""
from typing import Optional
from sqlalchemy.orm import Session

from linkedin_insights.models.insight import Insight, ScraperRun
from linkedin_insights.schemas.scraper import ScrapeRequest
from linkedin_insights.scraper.linkedin_scraper import LinkedInScraper
from linkedin_insights.services.insight_service import InsightService


class ScraperService:
    """Service for scraper business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.insight_service = InsightService(db)
        self.scraper = LinkedInScraper()
    
    def scrape_profile(self, request: ScrapeRequest) -> dict:
        """Scrape LinkedIn profile and save insight"""
        # Create scraper run record
        scraper_run = ScraperRun(
            insight_id=0,  # Will be updated after insight creation
            status="running"
        )
        self.db.add(scraper_run)
        self.db.commit()
        
        try:
            # Scrape profile
            scraped_data = self.scraper.scrape(str(request.profile_url))
            
            # Create or update insight
            insight = self.insight_service.create_insight(
                scraped_data
            )
            
            # Update scraper run
            scraper_run.insight_id = insight.id
            scraper_run.status = "completed"
            self.db.commit()
            
            return {
                "insight_id": insight.id,
                "status": "success",
                "message": "Profile scraped successfully"
            }
        except Exception as e:
            scraper_run.status = "failed"
            scraper_run.error_message = str(e)
            self.db.commit()
            raise

