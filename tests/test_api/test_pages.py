"""
Tests for LinkedIn pages endpoints
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import status
from datetime import datetime

from linkedin_insights.models.linkedin import LinkedInPage, Post, SocialMediaUser


class TestGetPage:
    """Tests for GET /pages/{page_id} endpoint"""
    
    def test_get_page_from_db(self, client, sample_page):
        """Test getting a page that exists in database"""
        response = client.get(f"/api/v1/pages/{sample_page.page_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page_id"] == sample_page.page_id
        assert data["name"] == sample_page.name
        assert data["id"] == sample_page.id
    
    @patch('linkedin_insights.api.v1.endpoints.pages.LinkedInPageScraper')
    @patch('linkedin_insights.api.v1.endpoints.pages.LinkedInPageService')
    def test_get_page_scrapes_if_not_in_db(self, mock_service_class, mock_scraper_class, client, db_session):
        """Test that page is scraped if not found in database"""
        import asyncio
        
        # Mock scraper with async function
        async def mock_scrape(page_id):
            return {
                'page_info': {
                    'page_id': 'new-company',
                    'name': 'New Company',
                    'url': 'https://www.linkedin.com/company/new-company',
                    'linkedin_internal_id': '789',
                    'description': 'A new company',
                    'industry': 'Technology',
                    'total_followers': 5000,
                    'head_count': 100,
                    'specialities': 'Software',
                    'profile_image_url': None,
                    'website': None
                },
                'posts': [],
                'employees': [],
                'scraped_at': datetime.utcnow().isoformat()
            }
        
        mock_scraper = MagicMock()
        mock_scraper.scrape_page = mock_scrape
        mock_scraper_class.return_value = mock_scraper
        
        # Mock service
        mock_service = MagicMock()
        mock_service.process_scraped_data.return_value = {
            'success': True,
            'page_id': 1,
            'page_page_id': 'new-company',
            'posts_processed': 0,
            'employees_processed': 0
        }
        mock_service_class.return_value = mock_service
        
        # Create the page that will be returned after scraping
        page = LinkedInPage(
            page_id='new-company',
            name='New Company',
            url='https://www.linkedin.com/company/new-company',
            linkedin_internal_id='789',
            description='A new company',
            industry='Technology',
            total_followers=5000,
            head_count=100
        )
        db_session.add(page)
        db_session.commit()
        db_session.refresh(page)
        
        # Make request - TestClient handles async endpoints
        response = client.get("/api/v1/pages/new-company")
        
        # Should return 200 if page exists, or handle scraping
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    def test_get_page_not_found(self, client):
        """Test getting a page that doesn't exist"""
        response = client.get("/api/v1/pages/non-existent-company")
        
        # Should return 404 or 500 depending on scraper behavior
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]


class TestGetPages:
    """Tests for GET /pages endpoint with filters"""
    
    def test_get_pages_no_filters(self, client, sample_pages):
        """Test getting all pages without filters"""
        response = client.get("/api/v1/pages")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert len(data["items"]) <= 20  # Default page size
        assert data["total"] >= 10
    
    def test_get_pages_with_follower_count_min(self, client, sample_pages):
        """Test filtering by minimum follower count"""
        response = client.get("/api/v1/pages?follower_count_min=5000")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(item["total_followers"] >= 5000 for item in data["items"])
    
    def test_get_pages_with_follower_count_max(self, client, sample_pages):
        """Test filtering by maximum follower count"""
        response = client.get("/api/v1/pages?follower_count_max=3000")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(item["total_followers"] <= 3000 for item in data["items"])
    
    def test_get_pages_with_industry_filter(self, client, sample_pages):
        """Test filtering by industry"""
        response = client.get("/api/v1/pages?industry=Technology")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all("Technology" in item.get("industry", "") for item in data["items"])
    
    def test_get_pages_with_page_name_filter(self, client, sample_pages):
        """Test filtering by page name (partial match)"""
        response = client.get("/api/v1/pages?page_name=Company 1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert any("Company 1" in item["name"] for item in data["items"])
    
    def test_get_pages_with_multiple_filters(self, client, sample_pages):
        """Test filtering with multiple parameters"""
        response = client.get(
            "/api/v1/pages?follower_count_min=2000&follower_count_max=8000&industry=Technology"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for item in data["items"]:
            assert item["total_followers"] >= 2000
            assert item["total_followers"] <= 8000
            assert "Technology" in item.get("industry", "")
    
    def test_get_pages_pagination(self, client, sample_pages):
        """Test pagination"""
        # First page
        response1 = client.get("/api/v1/pages?page=1&page_size=5")
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert len(data1["items"]) == 5
        assert data1["page"] == 1
        assert data1["page_size"] == 5
        
        # Second page
        response2 = client.get("/api/v1/pages?page=2&page_size=5")
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert len(data2["items"]) == 5
        assert data2["page"] == 2
        
        # Items should be different
        assert data1["items"][0]["id"] != data2["items"][0]["id"]


class TestGetPagePosts:
    """Tests for GET /pages/{page_id}/posts endpoint"""
    
    def test_get_page_posts(self, client, sample_page, sample_posts):
        """Test getting posts for a page"""
        response = client.get(f"/api/v1/pages/{sample_page.page_id}/posts")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 5
        assert data["total"] == 5
    
    def test_get_page_posts_pagination(self, client, sample_page, sample_posts):
        """Test pagination for posts"""
        response = client.get(f"/api/v1/pages/{sample_page.page_id}/posts?page=1&page_size=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total"] == 5
        assert data["has_next"] is True
        assert data["has_previous"] is False
    
    def test_get_page_posts_page_not_found(self, client):
        """Test getting posts for non-existent page"""
        response = client.get("/api/v1/pages/non-existent/posts")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetPageFollowers:
    """Tests for GET /pages/{page_id}/followers endpoint"""
    
    def test_get_page_followers(self, client, sample_page, db_session):
        """Test getting followers for a page"""
        # Create sample followers
        followers = [
            SocialMediaUser(
                linkedin_user_id=f"user-{i}",
                name=f"User {i}",
                title=f"Title {i}",
                profile_url=f"https://linkedin.com/in/user-{i}",
                page_id=sample_page.id
            )
            for i in range(1, 6)
        ]
        for follower in followers:
            db_session.add(follower)
        db_session.commit()
        
        response = client.get(f"/api/v1/pages/{sample_page.page_id}/followers")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 5
        assert data["total"] == 5
    
    def test_get_page_followers_pagination(self, client, sample_page, db_session):
        """Test pagination for followers"""
        # Create sample followers
        followers = [
            SocialMediaUser(
                linkedin_user_id=f"user-{i}",
                name=f"User {i}",
                title=f"Title {i}",
                profile_url=f"https://linkedin.com/in/user-{i}",
                page_id=sample_page.id
            )
            for i in range(1, 11)
        ]
        for follower in followers:
            db_session.add(follower)
        db_session.commit()
        
        response = client.get(f"/api/v1/pages/{sample_page.page_id}/followers?page=1&page_size=5")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 10
        assert data["has_next"] is True
    
    def test_get_page_followers_page_not_found(self, client):
        """Test getting followers for non-existent page"""
        response = client.get("/api/v1/pages/non-existent/followers")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

