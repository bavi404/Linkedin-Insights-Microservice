"""
Tests for pagination utility
"""
import pytest
from sqlalchemy.orm import Query

from linkedin_insights.utils.pagination import (
    PaginationParams,
    PaginationResult,
    paginate_query,
    paginate_query_with_filters,
    create_pagination_metadata,
)


class TestPaginationParams:
    """Tests for PaginationParams class"""
    
    def test_pagination_params_defaults(self):
        """Test default values"""
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 20
    
    def test_pagination_params_custom(self):
        """Test custom values"""
        params = PaginationParams(page=2, page_size=10)
        assert params.page == 2
        assert params.page_size == 10
    
    def test_pagination_params_skip(self):
        """Test skip calculation"""
        params = PaginationParams(page=1, page_size=20)
        assert params.skip == 0
        
        params = PaginationParams(page=2, page_size=20)
        assert params.skip == 20
        
        params = PaginationParams(page=3, page_size=10)
        assert params.skip == 20
    
    def test_pagination_params_limit(self):
        """Test limit property"""
        params = PaginationParams(page_size=15)
        assert params.limit == 15


class TestPaginationResult:
    """Tests for PaginationResult class"""
    
    def test_pagination_result_properties(self):
        """Test pagination result properties"""
        items = [1, 2, 3, 4, 5]
        result = PaginationResult(
            items=items,
            total_count=50,
            page=1,
            page_size=10
        )
        
        assert result.items == items
        assert result.total_count == 50
        assert result.page == 1
        assert result.page_size == 10
        assert result.total_pages == 5
        assert result.has_next is True
        assert result.has_previous is False
    
    def test_pagination_result_no_next(self):
        """Test when there's no next page"""
        result = PaginationResult(
            items=[1, 2, 3],
            total_count=3,
            page=1,
            page_size=10
        )
        
        assert result.total_pages == 1
        assert result.has_next is False
        assert result.has_previous is False
    
    def test_pagination_result_has_previous(self):
        """Test when there's a previous page"""
        result = PaginationResult(
            items=[1, 2, 3],
            total_count=50,
            page=3,
            page_size=10
        )
        
        assert result.has_previous is True
        assert result.has_next is True
    
    def test_pagination_result_to_dict(self):
        """Test conversion to dictionary"""
        items = [1, 2, 3]
        result = PaginationResult(
            items=items,
            total_count=30,
            page=2,
            page_size=10
        )
        
        data = result.to_dict()
        
        assert data["items"] == items
        assert data["total"] == 30
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total_pages"] == 3
        assert data["has_next"] is True
        assert data["has_previous"] is True


class TestPaginateQuery:
    """Tests for paginate_query function"""
    
    def test_paginate_query_basic(self, db_session, sample_pages):
        """Test basic pagination"""
        from linkedin_insights.models.linkedin import LinkedInPage
        
        query = db_session.query(LinkedInPage)
        result = paginate_query(query, page=1, page_size=5)
        
        assert len(result.items) == 5
        assert result.total_count == 10
        assert result.page == 1
        assert result.page_size == 5
        assert result.total_pages == 2
    
    def test_paginate_query_second_page(self, db_session, sample_pages):
        """Test pagination on second page"""
        from linkedin_insights.models.linkedin import LinkedInPage
        
        query = db_session.query(LinkedInPage)
        result = paginate_query(query, page=2, page_size=5)
        
        assert len(result.items) == 5
        assert result.page == 2
        assert result.total_pages == 2
    
    def test_paginate_query_last_page(self, db_session, sample_pages):
        """Test pagination on last page"""
        from linkedin_insights.models.linkedin import LinkedInPage
        
        query = db_session.query(LinkedInPage)
        result = paginate_query(query, page=2, page_size=8)
        
        assert len(result.items) == 2  # Only 2 items left
        assert result.page == 2
        assert result.has_next is False
    
    def test_paginate_query_empty_result(self, db_session):
        """Test pagination with empty result"""
        from linkedin_insights.models.linkedin import LinkedInPage
        
        query = db_session.query(LinkedInPage).filter(LinkedInPage.page_id == "non-existent")
        result = paginate_query(query, page=1, page_size=10)
        
        assert len(result.items) == 0
        assert result.total_count == 0
        assert result.total_pages == 0
        assert result.has_next is False
        assert result.has_previous is False
    
    def test_paginate_query_invalid_page(self, db_session, sample_pages):
        """Test pagination with invalid page number"""
        from linkedin_insights.models.linkedin import LinkedInPage
        
        query = db_session.query(LinkedInPage)
        # Should default to page 1 if invalid
        result = paginate_query(query, page=0, page_size=10)
        
        assert result.page == 1
    
    def test_paginate_query_large_page_size(self, db_session, sample_pages):
        """Test pagination with page size exceeding limit"""
        from linkedin_insights.models.linkedin import LinkedInPage
        
        query = db_session.query(LinkedInPage)
        # Should cap at 100
        result = paginate_query(query, page=1, page_size=200)
        
        assert result.page_size == 100


class TestPaginateQueryWithFilters:
    """Tests for paginate_query_with_filters function"""
    
    def test_paginate_query_with_ordering(self, db_session, sample_pages):
        """Test pagination with ordering"""
        from linkedin_insights.models.linkedin import LinkedInPage
        
        query = db_session.query(LinkedInPage)
        pagination = PaginationParams(page=1, page_size=5)
        
        result = paginate_query_with_filters(
            query,
            pagination,
            order_by=LinkedInPage.total_followers.desc()
        )
        
        assert len(result.items) == 5
        # Check that items are ordered by followers descending
        followers = [item.total_followers for item in result.items]
        assert followers == sorted(followers, reverse=True)
    
    def test_paginate_query_without_ordering(self, db_session, sample_pages):
        """Test pagination without ordering"""
        from linkedin_insights.models.linkedin import LinkedInPage
        
        query = db_session.query(LinkedInPage)
        pagination = PaginationParams(page=1, page_size=5)
        
        result = paginate_query_with_filters(query, pagination)
        
        assert len(result.items) == 5


class TestCreatePaginationMetadata:
    """Tests for create_pagination_metadata function"""
    
    def test_create_pagination_metadata(self):
        """Test creating pagination metadata"""
        metadata = create_pagination_metadata(total_count=100, page=2, page_size=20)
        
        assert metadata["total"] == 100
        assert metadata["page"] == 2
        assert metadata["page_size"] == 20
        assert metadata["total_pages"] == 5
        assert metadata["has_next"] is True
        assert metadata["has_previous"] is True
    
    def test_create_pagination_metadata_no_items(self):
        """Test metadata with no items"""
        metadata = create_pagination_metadata(total_count=0, page=1, page_size=20)
        
        assert metadata["total"] == 0
        assert metadata["total_pages"] == 0
        assert metadata["has_next"] is False
        assert metadata["has_previous"] is False
    
    def test_create_pagination_metadata_last_page(self):
        """Test metadata on last page"""
        metadata = create_pagination_metadata(total_count=50, page=5, page_size=10)
        
        assert metadata["total_pages"] == 5
        assert metadata["has_next"] is False
        assert metadata["has_previous"] is True
    
    def test_create_pagination_metadata_first_page(self):
        """Test metadata on first page"""
        metadata = create_pagination_metadata(total_count=50, page=1, page_size=10)
        
        assert metadata["has_next"] is True
        assert metadata["has_previous"] is False

