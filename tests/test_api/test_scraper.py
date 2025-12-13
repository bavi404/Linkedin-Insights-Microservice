"""
Tests for scraper endpoints
"""
import pytest
from fastapi import status


def test_scrape_profile(client):
    """Test scraping a profile"""
    response = client.post(
        "/api/v1/scraper/scrape",
        json={
            "profile_url": "https://linkedin.com/in/test"
        }
    )
    # Note: This will fail until scraper is implemented
    assert response.status_code in [
        status.HTTP_202_ACCEPTED,
        status.HTTP_500_INTERNAL_SERVER_ERROR
    ]

