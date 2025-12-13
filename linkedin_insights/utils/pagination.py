"""
Pagination utilities for FastAPI
Reusable pagination helpers for SQLAlchemy queries
"""
from typing import TypeVar, Generic, List, Dict, Any, Optional
from fastapi import Query
from sqlalchemy.orm import Query as SQLAlchemyQuery
from sqlalchemy import func

from linkedin_insights.schemas.linkedin import PaginatedResponseBase

T = TypeVar('T')


class PaginationParams:
    """Pagination parameters for FastAPI dependency injection"""
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page")
    ):
        self.page = page
        self.page_size = page_size
    
    @property
    def skip(self) -> int:
        """Calculate skip offset"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit (same as page_size)"""
        return self.page_size


class PaginationResult(Generic[T]):
    """Pagination result container"""
    
    def __init__(
        self,
        items: List[T],
        total_count: int,
        page: int,
        page_size: int
    ):
        self.items = items
        self.total_count = total_count
        self.page = page
        self.page_size = page_size
    
    @property
    def total_pages(self) -> int:
        """Calculate total pages"""
        if self.total_count == 0:
            return 0
        return (self.total_count + self.page_size - 1) // self.page_size
    
    @property
    def has_next(self) -> bool:
        """Check if there is a next page"""
        return self.page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page"""
        return self.page > 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            'items': self.items,
            'total': self.total_count,
            'page': self.page,
            'page_size': self.page_size,
            'total_pages': self.total_pages,
            'has_next': self.has_next,
            'has_previous': self.has_previous,
        }


def paginate_query(
    query: SQLAlchemyQuery,
    page: int = 1,
    page_size: int = 20
) -> PaginationResult:
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        page_size: Number of items per page
    
    Returns:
        PaginationResult with items and metadata
    
    Example:
        ```python
        query = db.query(LinkedInPage)
        result = paginate_query(query, page=1, page_size=20)
        return result.to_dict()
        ```
    """
    # Validate inputs
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > 100:
        page_size = 100
    
    # Get total count (before pagination)
    total_count = query.count()
    
    # Calculate skip
    skip = (page - 1) * page_size
    
    # Apply pagination
    items = query.offset(skip).limit(page_size).all()
    
    return PaginationResult(
        items=items,
        total_count=total_count,
        page=page,
        page_size=page_size
    )


def paginate_query_with_filters(
    query: SQLAlchemyQuery,
    pagination: PaginationParams,
    order_by: Optional[Any] = None
) -> PaginationResult:
    """
    Paginate a SQLAlchemy query with optional ordering
    
    Args:
        query: SQLAlchemy query object
        pagination: PaginationParams instance
        order_by: Optional column to order by (e.g., Model.created_at.desc())
    
    Returns:
        PaginationResult with items and metadata
    
    Example:
        ```python
        query = db.query(Post).filter(Post.page_id == page_id)
        pagination = PaginationParams(page=1, page_size=15)
        result = paginate_query_with_filters(query, pagination, order_by=Post.posted_at.desc())
        return result.to_dict()
        ```
    """
    # Apply ordering if provided
    if order_by is not None:
        query = query.order_by(order_by)
    
    return paginate_query(query, pagination.page, pagination.page_size)


def create_pagination_metadata(
    total_count: int,
    page: int,
    page_size: int
) -> Dict[str, Any]:
    """
    Create pagination metadata dictionary
    
    Args:
        total_count: Total number of items
        page: Current page number
        page_size: Items per page
    
    Returns:
        Dictionary with pagination metadata
    """
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
    
    return {
        'total': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_previous': page > 1,
    }


def get_pagination_dependency(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
) -> PaginationParams:
    """
    FastAPI dependency for pagination parameters
    
    Usage:
        ```python
        @router.get("/items")
        def get_items(pagination: PaginationParams = Depends(get_pagination_dependency)):
            query = db.query(Item)
            result = paginate_query(query, pagination.page, pagination.page_size)
            return result.to_dict()
        ```
    """
    return PaginationParams(page=page, page_size=page_size)

