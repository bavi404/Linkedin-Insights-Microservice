"""
Tests for LinkedIn scraper
"""
import pytest
from linkedin_insights.scraper.linkedin_scraper import LinkedInScraper


def test_scraper_initialization():
    """Test scraper initialization"""
    scraper = LinkedInScraper()
    assert scraper.timeout > 0
    assert scraper.retry_attempts > 0

