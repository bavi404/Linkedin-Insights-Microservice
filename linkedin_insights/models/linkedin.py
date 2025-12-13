"""
LinkedIn models
SQLAlchemy ORM models for LinkedIn pages, users, posts, and comments
"""
from sqlalchemy import (
    Column, String, Integer, Text, ForeignKey, DateTime, 
    Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from linkedin_insights.models.base import BaseModel


class LinkedInPage(BaseModel):
    """LinkedIn company/page model"""
    __tablename__ = "linkedin_pages"
    
    # Unique identifier from LinkedIn
    page_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(500), nullable=False, unique=True, index=True)
    linkedin_internal_id = Column(String(100), nullable=True, index=True)
    
    # Company details
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    industry = Column(String(255), nullable=True, index=True)
    
    # Metrics
    total_followers = Column(Integer, nullable=True, default=0)
    head_count = Column(Integer, nullable=True)
    
    # Additional data
    specialities = Column(Text, nullable=True)  # Comma-separated or JSON
    profile_image_url = Column(String(500), nullable=True)
    
    # Relationships
    users = relationship(
        "SocialMediaUser",
        back_populates="page",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    posts = relationship(
        "Post",
        back_populates="page",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_page_id", "page_id"),
        Index("idx_linkedin_internal_id", "linkedin_internal_id"),
        Index("idx_name_industry", "name", "industry"),
    )
    
    def __repr__(self) -> str:
        return f"<LinkedInPage(id={self.id}, page_id='{self.page_id}', name='{self.name}')>"


class SocialMediaUser(BaseModel):
    """Social media user model (LinkedIn users associated with pages)"""
    __tablename__ = "social_media_users"
    
    # LinkedIn user identifier
    linkedin_user_id = Column(String(100), nullable=False, index=True)
    
    # User information
    name = Column(String(255), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    profile_url = Column(String(500), nullable=False, index=True)
    
    # Foreign key to LinkedInPage
    page_id = Column(
        Integer,
        ForeignKey("linkedin_pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relationships
    page = relationship("LinkedInPage", back_populates="users")
    
    # Indexes
    __table_args__ = (
        Index("idx_linkedin_user_id", "linkedin_user_id"),
        Index("idx_page_user", "page_id", "linkedin_user_id"),
        UniqueConstraint("linkedin_user_id", "page_id", name="uq_user_page"),
    )
    
    def __repr__(self) -> str:
        return f"<SocialMediaUser(id={self.id}, linkedin_user_id='{self.linkedin_user_id}', name='{self.name}')>"


class Post(BaseModel):
    """LinkedIn post model"""
    __tablename__ = "posts"
    
    # Unique identifier from LinkedIn
    post_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign key to LinkedInPage
    page_id = Column(
        Integer,
        ForeignKey("linkedin_pages.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Post content
    content = Column(Text, nullable=True)
    
    # Engagement metrics
    like_count = Column(Integer, nullable=False, default=0, index=True)
    comment_count = Column(Integer, nullable=False, default=0, index=True)
    
    # Post timestamp from LinkedIn
    posted_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Relationships
    page = relationship("LinkedInPage", back_populates="posts")
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="dynamic",
        order_by="Comment.created_at"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_post_id", "post_id"),
        Index("idx_page_posted_at", "page_id", "posted_at"),
        Index("idx_engagement", "like_count", "comment_count"),
    )
    
    def __repr__(self) -> str:
        return f"<Post(id={self.id}, post_id='{self.post_id}', page_id={self.page_id}, likes={self.like_count})>"


class Comment(BaseModel):
    """LinkedIn post comment model"""
    __tablename__ = "comments"
    
    # Unique identifier from LinkedIn
    comment_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign key to Post
    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Comment information
    author_name = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    
    # Comment timestamp from LinkedIn
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    
    # Indexes
    __table_args__ = (
        Index("idx_comment_id", "comment_id"),
        Index("idx_post_created_at", "post_id", "created_at"),
        Index("idx_author", "author_name"),
    )
    
    def __repr__(self) -> str:
        return f"<Comment(id={self.id}, comment_id='{self.comment_id}', post_id={self.post_id}, author='{self.author_name}')>"

