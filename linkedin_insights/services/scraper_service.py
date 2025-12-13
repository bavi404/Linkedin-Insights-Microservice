"""
Scraper Service Wrapper
Async wrapper for Playwright scraper
"""
import logging
from typing import Dict, Any

from linkedin_insights.scraper.page_scraper import LinkedInPageScraper

logger = logging.getLogger(__name__)


class ScraperService:
    """Async service wrapper for LinkedIn page scraper"""
    
    def __init__(self):
        self.scraper = LinkedInPageScraper()
    
    async def scrape_linkedin_page(self, page_id: str) -> Dict[str, Any]:
        """
        Scrape LinkedIn page (async)
        
        Args:
            page_id: Last part of LinkedIn company URL
        
        Returns:
            Dictionary with page info, posts, comments, and employees
        """
        try:
            return await self.scraper.scrape_page(page_id)
        except Exception as e:
            logger.error(f"Error in scraper service: {str(e)}", exc_info=True)
            return {
                'error': True,
                'error_message': str(e),
                'page_info': None,
                'posts': [],
                'employees': [],
                'scraped_at': None
            }
