"""
Scraper Service Wrapper
Synchronous wrapper for async Playwright scraper
"""
import asyncio
import logging
from typing import Dict, Any

from linkedin_insights.scraper.page_scraper import LinkedInPageScraper

logger = logging.getLogger(__name__)


class ScraperService:
    """Synchronous service wrapper for async LinkedIn page scraper"""
    
    def __init__(self):
        self.scraper = LinkedInPageScraper()
    
    def scrape_linkedin_page(self, page_id: str) -> Dict[str, Any]:
        """
        Scrape LinkedIn page (synchronous wrapper)
        
        Args:
            page_id: Last part of LinkedIn company URL
        
        Returns:
            Dictionary with page info, posts, comments, and employees
        """
        try:
            # Try to get existing event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, use nest_asyncio if available
                    try:
                        import nest_asyncio
                        nest_asyncio.apply()
                        return loop.run_until_complete(self.scraper.scrape_page(page_id))
                    except ImportError:
                        logger.warning("nest_asyncio not installed. Cannot run in existing event loop.")
                        raise RuntimeError("Cannot run async scraper in existing event loop")
                
                return loop.run_until_complete(self.scraper.scrape_page(page_id))
            
            except RuntimeError:
                # No event loop, create a new one
                return asyncio.run(self.scraper.scrape_page(page_id))
        
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

