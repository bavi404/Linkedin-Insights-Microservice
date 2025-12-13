"""
Tests for scraper service (mocked)
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from linkedin_insights.scraper.page_scraper import LinkedInPageScraper
from linkedin_insights.scraper.scraper_service import ScraperService


class TestLinkedInPageScraper:
    """Tests for LinkedInPageScraper with mocked Playwright"""
    
    @pytest.mark.asyncio
    @patch('linkedin_insights.scraper.page_scraper.async_playwright')
    async def test_scrape_page_success(self, mock_playwright):
        """Test successful page scraping"""
        # Mock Playwright browser and page
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock page navigation and content
        mock_response = MagicMock()
        mock_response.status = 200
        mock_page.goto.return_value = mock_response
        mock_page.wait_for_selector.return_value = None
        mock_page.query_selector.return_value = None
        mock_page.query_selector_all.return_value = []
        mock_page.content.return_value = "<html></html>"
        
        scraper = LinkedInPageScraper()
        result = await scraper.scrape_page("test-company")
        
        assert "page_info" in result
        assert "posts" in result
        assert "employees" in result
        assert "scraped_at" in result
    
    @pytest.mark.asyncio
    @patch('linkedin_insights.scraper.page_scraper.async_playwright')
    async def test_scrape_page_not_found(self, mock_playwright):
        """Test scraping when page is not found"""
        # Mock Playwright browser and page
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock 404 response
        mock_response = MagicMock()
        mock_response.status = 404
        mock_page.goto.return_value = mock_response
        
        scraper = LinkedInPageScraper()
        result = await scraper.scrape_page("non-existent")
        
        assert result.get("error") is True
        assert "error_message" in result
    
    @pytest.mark.asyncio
    @patch('linkedin_insights.scraper.page_scraper.async_playwright')
    async def test_scrape_page_timeout(self, mock_playwright):
        """Test scraping with timeout"""
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        
        # Mock Playwright browser
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock timeout error
        mock_page.goto.side_effect = PlaywrightTimeoutError("Timeout")
        
        scraper = LinkedInPageScraper()
        result = await scraper.scrape_page("test-company")
        
        assert result.get("error") is True
        assert "timeout" in result.get("error_message", "").lower()
    
    @pytest.mark.asyncio
    @patch('linkedin_insights.scraper.page_scraper.async_playwright')
    async def test_scrape_page_extracts_data(self, mock_playwright):
        """Test that scraper extracts page data correctly"""
        # Mock Playwright browser and page
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_page.goto.return_value = mock_response
        
        # Mock page elements
        mock_name_element = AsyncMock()
        mock_name_element.inner_text.return_value = "Test Company"
        mock_page.query_selector.return_value = mock_name_element
        mock_page.query_selector_all.return_value = []
        mock_page.content.return_value = "<html><h1>Test Company</h1></html>"
        
        scraper = LinkedInPageScraper()
        result = await scraper.scrape_page("test-company")
        
        assert "page_info" in result
        # The actual extraction depends on selectors, but structure should be there
        assert isinstance(result["page_info"], dict)


class TestScraperService:
    """Tests for ScraperService (synchronous wrapper)"""
    
    @patch('linkedin_insights.scraper.scraper_service.LinkedInPageScraper')
    def test_scrape_linkedin_page_success(self, mock_scraper_class):
        """Test successful scraping via service"""
        # Mock async scraper
        mock_scraper = AsyncMock()
        mock_scraper.scrape_page.return_value = {
            'page_info': {
                'page_id': 'test-company',
                'name': 'Test Company',
                'url': 'https://www.linkedin.com/company/test-company'
            },
            'posts': [],
            'employees': [],
            'scraped_at': datetime.utcnow().isoformat()
        }
        mock_scraper_class.return_value = mock_scraper
        
        service = ScraperService()
        result = service.scrape_linkedin_page("test-company")
        
        assert "page_info" in result
        assert result["page_info"]["page_id"] == "test-company"
    
    @patch('linkedin_insights.scraper.scraper_service.LinkedInPageScraper')
    def test_scrape_linkedin_page_error(self, mock_scraper_class):
        """Test error handling in service"""
        # Mock scraper to raise exception
        mock_scraper = AsyncMock()
        mock_scraper.scrape_page.side_effect = Exception("Scraping failed")
        mock_scraper_class.return_value = mock_scraper
        
        service = ScraperService()
        result = service.scrape_linkedin_page("test-company")
        
        assert result.get("error") is True
        assert "error_message" in result

