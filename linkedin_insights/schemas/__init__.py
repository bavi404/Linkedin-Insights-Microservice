"""Schemas module - Pydantic schemas for request/response validation"""

from linkedin_insights.schemas.base import BaseSchema, TimestampSchema
from linkedin_insights.schemas.insight import (
    InsightBase,
    InsightCreate,
    InsightUpdate,
    InsightResponse,
    InsightListResponse,
)
from linkedin_insights.schemas.scraper import (
    ScrapeRequest,
    ScrapeResponse,
    ScraperRunResponse,
)
from linkedin_insights.schemas.ai_summary import (
    PageStatsRequest,
    AISummaryResponse,
    AISummaryErrorResponse,
)
from linkedin_insights.schemas.linkedin import (
    # Comment schemas
    CommentBase,
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    # Post schemas
    PostBase,
    PostCreate,
    PostUpdate,
    PostResponse,
    PostWithComments,
    # SocialMediaUser schemas
    SocialMediaUserBase,
    SocialMediaUserCreate,
    SocialMediaUserUpdate,
    SocialMediaUserResponse,
    # LinkedInPage schemas
    LinkedInPageBase,
    LinkedInPageCreate,
    LinkedInPageUpdate,
    LinkedInPageResponse,
    LinkedInPageWithPosts,
    LinkedInPageWithEmployees,
    LinkedInPageWithPostsAndComments,
    LinkedInPageFull,
    # Paginated response schemas
    PaginatedResponseBase,
    PaginatedCommentResponse,
    PaginatedPostResponse,
    PaginatedPostWithCommentsResponse,
    PaginatedSocialMediaUserResponse,
    PaginatedLinkedInPageResponse,
)

__all__ = [
    # Base
    "BaseSchema",
    "TimestampSchema",
    # Insight
    "InsightBase",
    "InsightCreate",
    "InsightUpdate",
    "InsightResponse",
    "InsightListResponse",
    # Scraper
    "ScrapeRequest",
    "ScrapeResponse",
    "ScraperRunResponse",
    # AI Summary
    "PageStatsRequest",
    "AISummaryResponse",
    "AISummaryErrorResponse",
    # Comment
    "CommentBase",
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
    # Post
    "PostBase",
    "PostCreate",
    "PostUpdate",
    "PostResponse",
    "PostWithComments",
    # SocialMediaUser
    "SocialMediaUserBase",
    "SocialMediaUserCreate",
    "SocialMediaUserUpdate",
    "SocialMediaUserResponse",
    # LinkedInPage
    "LinkedInPageBase",
    "LinkedInPageCreate",
    "LinkedInPageUpdate",
    "LinkedInPageResponse",
    "LinkedInPageWithPosts",
    "LinkedInPageWithEmployees",
    "LinkedInPageWithPostsAndComments",
    "LinkedInPageFull",
    # Paginated
    "PaginatedResponseBase",
    "PaginatedCommentResponse",
    "PaginatedPostResponse",
    "PaginatedPostWithCommentsResponse",
    "PaginatedSocialMediaUserResponse",
    "PaginatedLinkedInPageResponse",
]
