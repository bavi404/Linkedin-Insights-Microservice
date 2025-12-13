"""
LinkedIn schemas
Pydantic schemas for LinkedIn models (Page, User, Post, Comment)
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field, HttpUrl, ConfigDict

from linkedin_insights.schemas.base import BaseSchema, TimestampSchema


# ============================================================================
# Comment Schemas
# ============================================================================

class CommentBase(BaseSchema):
    """Base comment schema"""
    comment_id: str = Field(..., description="Unique comment identifier from LinkedIn")
    author_name: str = Field(..., max_length=255, description="Comment author name")
    content: str = Field(..., description="Comment content")
    created_at: datetime = Field(..., description="Comment creation timestamp from LinkedIn")


class CommentCreate(CommentBase):
    """Schema for creating a comment"""
    post_id: int = Field(..., description="ID of the post this comment belongs to")


class CommentUpdate(BaseSchema):
    """Schema for updating a comment"""
    author_name: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None


class CommentResponse(CommentBase):
    """Schema for comment response"""
    id: int
    post_id: int
    updated_at: datetime = Field(..., description="Last update timestamp from database")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Post Schemas
# ============================================================================

class PostBase(BaseSchema):
    """Base post schema"""
    post_id: str = Field(..., description="Unique post identifier from LinkedIn")
    content: Optional[str] = Field(None, description="Post content")
    like_count: int = Field(0, ge=0, description="Number of likes")
    comment_count: int = Field(0, ge=0, description="Number of comments")
    posted_at: datetime = Field(..., description="Post timestamp from LinkedIn")


class PostCreate(PostBase):
    """Schema for creating a post"""
    page_id: int = Field(..., description="ID of the page this post belongs to")


class PostUpdate(BaseSchema):
    """Schema for updating a post"""
    content: Optional[str] = None
    like_count: Optional[int] = Field(None, ge=0)
    comment_count: Optional[int] = Field(None, ge=0)


class PostResponse(PostBase, TimestampSchema):
    """Schema for post response (without nested comments)"""
    id: int
    page_id: int
    
    model_config = ConfigDict(from_attributes=True)


class PostWithComments(PostResponse):
    """Schema for post response with nested comments"""
    comments: List[CommentResponse] = Field(default_factory=list, description="List of comments on this post")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# SocialMediaUser Schemas
# ============================================================================

class SocialMediaUserBase(BaseSchema):
    """Base social media user schema"""
    linkedin_user_id: str = Field(..., max_length=100, description="LinkedIn user identifier")
    name: str = Field(..., max_length=255, description="User name")
    title: Optional[str] = Field(None, max_length=500, description="User job title")
    profile_url: HttpUrl = Field(..., description="User profile URL")


class SocialMediaUserCreate(SocialMediaUserBase):
    """Schema for creating a social media user"""
    page_id: int = Field(..., description="ID of the page this user belongs to")


class SocialMediaUserUpdate(BaseSchema):
    """Schema for updating a social media user"""
    name: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, max_length=500)
    profile_url: Optional[HttpUrl] = None


class SocialMediaUserResponse(SocialMediaUserBase, TimestampSchema):
    """Schema for social media user response"""
    id: int
    page_id: int
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# LinkedInPage Schemas
# ============================================================================

class LinkedInPageBase(BaseSchema):
    """Base LinkedIn page schema"""
    page_id: str = Field(..., max_length=100, description="Unique page identifier from LinkedIn")
    name: str = Field(..., max_length=255, description="Page name")
    url: HttpUrl = Field(..., description="Page URL")
    linkedin_internal_id: Optional[str] = Field(None, max_length=100, description="LinkedIn internal identifier")
    description: Optional[str] = Field(None, description="Page description")
    website: Optional[HttpUrl] = Field(None, description="Company website")
    industry: Optional[str] = Field(None, max_length=255, description="Industry")
    total_followers: Optional[int] = Field(None, ge=0, description="Total number of followers")
    head_count: Optional[int] = Field(None, ge=0, description="Company head count")
    specialities: Optional[str] = Field(None, description="Company specialities")
    profile_image_url: Optional[HttpUrl] = Field(None, description="Profile image URL")


class LinkedInPageCreate(LinkedInPageBase):
    """Schema for creating a LinkedIn page"""
    pass


class LinkedInPageUpdate(BaseSchema):
    """Schema for updating a LinkedIn page"""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    industry: Optional[str] = Field(None, max_length=255)
    total_followers: Optional[int] = Field(None, ge=0)
    head_count: Optional[int] = Field(None, ge=0)
    specialities: Optional[str] = None
    profile_image_url: Optional[HttpUrl] = None


class LinkedInPageResponse(LinkedInPageBase, TimestampSchema):
    """Schema for LinkedIn page response (without nested data)"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class LinkedInPageWithPosts(LinkedInPageResponse):
    """Schema for LinkedIn page response with nested posts"""
    posts: List[PostResponse] = Field(default_factory=list, description="List of posts from this page")
    
    model_config = ConfigDict(from_attributes=True)


class LinkedInPageWithEmployees(LinkedInPageResponse):
    """Schema for LinkedIn page response with nested employees"""
    employees: List[SocialMediaUserResponse] = Field(default_factory=list, description="List of employees/users associated with this page")
    
    model_config = ConfigDict(from_attributes=True)


class LinkedInPageWithPostsAndComments(LinkedInPageResponse):
    """Schema for LinkedIn page response with nested posts and comments"""
    posts: List[PostWithComments] = Field(default_factory=list, description="List of posts with their comments")
    
    model_config = ConfigDict(from_attributes=True)


class LinkedInPageFull(LinkedInPageResponse):
    """Schema for full LinkedIn page response with all nested data"""
    posts: List[PostWithComments] = Field(default_factory=list, description="List of posts with their comments")
    employees: List[SocialMediaUserResponse] = Field(default_factory=list, description="List of employees/users")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Paginated Response Schemas
# ============================================================================

class PaginatedResponseBase(BaseSchema):
    """Base paginated response schema"""
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    
    model_config = ConfigDict(from_attributes=True)


class PaginatedCommentResponse(PaginatedResponseBase):
    """Paginated response for comments"""
    items: List[CommentResponse] = Field(..., description="List of comments")


class PaginatedPostResponse(PaginatedResponseBase):
    """Paginated response for posts"""
    items: List[PostResponse] = Field(..., description="List of posts")


class PaginatedPostWithCommentsResponse(PaginatedResponseBase):
    """Paginated response for posts with nested comments"""
    items: List[PostWithComments] = Field(..., description="List of posts with comments")


class PaginatedSocialMediaUserResponse(PaginatedResponseBase):
    """Paginated response for social media users"""
    items: List[SocialMediaUserResponse] = Field(..., description="List of social media users")


class PaginatedLinkedInPageResponse(PaginatedResponseBase):
    """Paginated response for LinkedIn pages"""
    items: List[LinkedInPageResponse] = Field(..., description="List of LinkedIn pages")

