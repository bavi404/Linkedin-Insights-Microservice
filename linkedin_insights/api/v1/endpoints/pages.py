"""
LinkedIn Pages endpoints
Endpoints for LinkedIn company pages
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from linkedin_insights.db.base import get_db
from linkedin_insights.db.repositories import LinkedInPageRepository, PostRepository, SocialMediaUserRepository
from linkedin_insights.models.linkedin import LinkedInPage, Post, SocialMediaUser
from linkedin_insights.schemas.linkedin import (
    LinkedInPageResponse,
    PaginatedLinkedInPageResponse,
    PaginatedPostResponse,
    PaginatedSocialMediaUserResponse,
)
from linkedin_insights.services.linkedin_page_service import LinkedInPageService
from linkedin_insights.scraper.page_scraper import LinkedInPageScraper
from linkedin_insights.utils.pagination import (
    PaginationParams,
    paginate_query,
    paginate_query_with_filters,
    get_pagination_dependency,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{page_id}", response_model=LinkedInPageResponse, status_code=status.HTTP_200_OK)
async def get_page(
    page_id: str,
    db: Session = Depends(get_db)
):
    """
    Get LinkedIn page by page_id
    
    - If page exists in DB → return from DB
    - If not → scrape LinkedIn, store in DB, return response
    """
    page_repo = LinkedInPageRepository(LinkedInPage, db)
    
    # Check if page exists in DB
    page = page_repo.get_by_page_id(page_id)
    
    if page:
        logger.info(f"Page {page_id} found in database")
        return page
    
    # Page not found, scrape it
    logger.info(f"Page {page_id} not found in database, scraping...")
    
    try:
        scraper = LinkedInPageScraper()
        scraped_data = await scraper.scrape_page(page_id)
        
        if scraped_data.get('error'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page not found or inaccessible: {scraped_data.get('error_message', 'Unknown error')}"
            )
        
        # Process and store scraped data
        service = LinkedInPageService(db)
        result = service.process_scraped_data(scraped_data)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process scraped data: {result.get('error', 'Unknown error')}"
            )
        
        # Fetch the newly created/updated page
        page = page_repo.get_by_page_id(page_id)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Page was scraped but not found in database"
            )
        
        logger.info(f"Successfully scraped and stored page {page_id}")
        return page
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping page {page_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scraping page: {str(e)}"
        )


@router.get("", response_model=PaginatedLinkedInPageResponse, status_code=status.HTTP_200_OK)
def get_pages(
    pagination: PaginationParams = Depends(get_pagination_dependency),
    follower_count_min: Optional[int] = Query(None, ge=0, description="Minimum follower count"),
    follower_count_max: Optional[int] = Query(None, ge=0, description="Maximum follower count"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    page_name: Optional[str] = Query(None, description="Filter by page name (partial match)"),
    db: Session = Depends(get_db)
):
    """
    Get list of LinkedIn pages with filters
    
    Filters:
    - follower_count_min: Minimum number of followers
    - follower_count_max: Maximum number of followers
    - industry: Filter by industry
    - page_name: Partial match on page name
    """
    # Build query with filters
    query = db.query(LinkedInPage)
    
    # Apply filters
    if follower_count_min is not None:
        query = query.filter(LinkedInPage.total_followers >= follower_count_min)
    
    if follower_count_max is not None:
        query = query.filter(LinkedInPage.total_followers <= follower_count_max)
    
    if industry:
        query = query.filter(LinkedInPage.industry.ilike(f"%{industry}%"))
    
    if page_name:
        query = query.filter(LinkedInPage.name.ilike(f"%{page_name}%"))
    
    # Use pagination utility
    result = paginate_query(query, pagination.page, pagination.page_size)
    
    return result.to_dict()


@router.get("/{page_id}/posts", response_model=PaginatedPostResponse, status_code=status.HTTP_200_OK)
def get_page_posts(
    page_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(15, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get posts for a LinkedIn page
    
    Returns recent 10-15 posts (default 15) with pagination support
    """
    page_repo = LinkedInPageRepository(LinkedInPage, db)
    
    # Get page by page_id
    linkedin_page = page_repo.get_by_page_id(page_id)
    if not linkedin_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page with page_id '{page_id}' not found"
        )
    
    # Get posts for this page with ordering
    query = db.query(Post).filter(Post.page_id == linkedin_page.id)
    
    # Use pagination utility with ordering
    pagination = PaginationParams(page=page, page_size=page_size)
    result = paginate_query_with_filters(
        query, 
        pagination, 
        order_by=Post.posted_at.desc()
    )
    
    return result.to_dict()


@router.get("/{page_id}/followers", response_model=PaginatedSocialMediaUserResponse, status_code=status.HTTP_200_OK)
def get_page_followers(
    page_id: str,
    pagination: PaginationParams = Depends(get_pagination_dependency),
    db: Session = Depends(get_db)
):
    """
    Get employees/followers for a LinkedIn page
    
    Returns list of employees/followers with pagination support
    """
    page_repo = LinkedInPageRepository(LinkedInPage, db)
    
    # Get page by page_id
    linkedin_page = page_repo.get_by_page_id(page_id)
    if not linkedin_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Page with page_id '{page_id}' not found"
        )
    
    # Get users/employees for this page
    query = db.query(SocialMediaUser).filter(SocialMediaUser.page_id == linkedin_page.id)
    
    # Use pagination utility
    result = paginate_query(query, pagination.page, pagination.page_size)
    
    return result.to_dict()

