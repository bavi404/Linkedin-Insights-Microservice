"""
LinkedIn model repositories
Async repository implementations for LinkedIn models with upsert capabilities
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, and_

from linkedin_insights.models.linkedin import (
    LinkedInPage,
    SocialMediaUser,
    Post,
    Comment,
)
from linkedin_insights.db.repository import BaseRepository


class LinkedInPageRepository(BaseRepository[LinkedInPage]):
    """Repository for LinkedInPage model with async upsert support"""
    
    async def get_by_page_id(self, page_id: str) -> Optional[LinkedInPage]:
        """Get page by LinkedIn page_id"""
        result = await self.db.execute(
            select(self.model).filter(self.model.page_id == page_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_url(self, url: str) -> Optional[LinkedInPage]:
        """Get page by URL"""
        result = await self.db.execute(
            select(self.model).filter(self.model.url == url)
        )
        return result.scalar_one_or_none()
    
    async def upsert(self, page_data: Dict[str, Any]) -> LinkedInPage:
        """
        Upsert page by page_id
        Creates if not exists, updates if exists
        """
        page_id = page_data.get('page_id')
        if not page_id:
            raise ValueError("page_id is required")
        
        # Try to find existing page
        existing_page = await self.get_by_page_id(page_id)
        
        if existing_page:
            # Update existing page
            for key, value in page_data.items():
                if key != 'page_id' and hasattr(existing_page, key):
                    setattr(existing_page, key, value)
            await self.db.commit()
            await self.db.refresh(existing_page)
            return existing_page
        else:
            # Create new page
            db_page = self.model(**page_data)
            self.db.add(db_page)
            await self.db.commit()
            await self.db.refresh(db_page)
            return db_page


class PostRepository(BaseRepository[Post]):
    """Repository for Post model with async upsert support"""
    
    async def get_by_post_id(self, post_id: str) -> Optional[Post]:
        """Get post by LinkedIn post_id"""
        result = await self.db.execute(
            select(self.model).filter(self.model.post_id == post_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_page_id(self, page_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        """Get posts by page_id"""
        result = await self.db.execute(
            select(self.model)
            .filter(self.model.page_id == page_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def upsert(self, post_data: Dict[str, Any], page_id: int) -> Post:
        """
        Upsert post by post_id
        Creates if not exists, updates if exists
        """
        post_id = post_data.get('post_id')
        if not post_id:
            raise ValueError("post_id is required")
        
        # Try to find existing post
        existing_post = await self.get_by_post_id(post_id)
        
        if existing_post:
            # Update existing post
            for key, value in post_data.items():
                if key not in ('post_id', 'page_id') and hasattr(existing_post, key):
                    setattr(existing_post, key, value)
            await self.db.commit()
            await self.db.refresh(existing_post)
            return existing_post
        else:
            # Create new post
            post_data['page_id'] = page_id
            db_post = self.model(**post_data)
            self.db.add(db_post)
            await self.db.commit()
            await self.db.refresh(db_post)
            return db_post
    
    async def upsert_batch(self, posts_data: List[Dict[str, Any]], page_id: int) -> List[Post]:
        """Upsert multiple posts in batch"""
        upserted_posts = []
        for post_data in posts_data:
            try:
                post = await self.upsert(post_data, page_id)
                upserted_posts.append(post)
            except IntegrityError:
                await self.db.rollback()
                # Retry once after rollback
                try:
                    post = await self.upsert(post_data, page_id)
                    upserted_posts.append(post)
                except Exception as e:
                    await self.db.rollback()
                    continue
            except Exception as e:
                await self.db.rollback()
                continue
        
        return upserted_posts


class CommentRepository(BaseRepository[Comment]):
    """Repository for Comment model with async upsert support"""
    
    async def get_by_comment_id(self, comment_id: str) -> Optional[Comment]:
        """Get comment by LinkedIn comment_id"""
        result = await self.db.execute(
            select(self.model).filter(self.model.comment_id == comment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_post_id(self, post_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get comments by post_id"""
        result = await self.db.execute(
            select(self.model)
            .filter(self.model.post_id == post_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def upsert(self, comment_data: Dict[str, Any], post_id: int) -> Comment:
        """
        Upsert comment by comment_id
        Creates if not exists, updates if exists
        """
        comment_id = comment_data.get('comment_id')
        if not comment_id:
            raise ValueError("comment_id is required")
        
        # Try to find existing comment
        existing_comment = await self.get_by_comment_id(comment_id)
        
        if existing_comment:
            # Update existing comment
            for key, value in comment_data.items():
                if key not in ('comment_id', 'post_id') and hasattr(existing_comment, key):
                    setattr(existing_comment, key, value)
            await self.db.commit()
            await self.db.refresh(existing_comment)
            return existing_comment
        else:
            # Create new comment
            comment_data['post_id'] = post_id
            db_comment = self.model(**comment_data)
            self.db.add(db_comment)
            await self.db.commit()
            await self.db.refresh(db_comment)
            return db_comment
    
    async def upsert_batch(self, comments_data: List[Dict[str, Any]], post_id: int) -> List[Comment]:
        """Upsert multiple comments in batch"""
        upserted_comments = []
        for comment_data in comments_data:
            try:
                comment = await self.upsert(comment_data, post_id)
                upserted_comments.append(comment)
            except IntegrityError:
                await self.db.rollback()
                # Retry once after rollback
                try:
                    comment = await self.upsert(comment_data, post_id)
                    upserted_comments.append(comment)
                except Exception as e:
                    await self.db.rollback()
                    continue
            except Exception as e:
                await self.db.rollback()
                continue
        
        return upserted_comments


class SocialMediaUserRepository(BaseRepository[SocialMediaUser]):
    """Repository for SocialMediaUser model with async upsert support"""
    
    async def get_by_linkedin_user_id(self, linkedin_user_id: str, page_id: int) -> Optional[SocialMediaUser]:
        """Get user by linkedin_user_id and page_id"""
        result = await self.db.execute(
            select(self.model).filter(
                and_(
                    self.model.linkedin_user_id == linkedin_user_id,
                    self.model.page_id == page_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_page_id(self, page_id: int, skip: int = 0, limit: int = 100) -> List[SocialMediaUser]:
        """Get users by page_id"""
        result = await self.db.execute(
            select(self.model)
            .filter(self.model.page_id == page_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def upsert(self, user_data: Dict[str, Any], page_id: int) -> SocialMediaUser:
        """
        Upsert user by linkedin_user_id and page_id
        Creates if not exists, updates if exists
        """
        linkedin_user_id = user_data.get('linkedin_user_id')
        if not linkedin_user_id:
            raise ValueError("linkedin_user_id is required")
        
        # Try to find existing user
        existing_user = await self.get_by_linkedin_user_id(linkedin_user_id, page_id)
        
        if existing_user:
            # Update existing user
            for key, value in user_data.items():
                if key not in ('linkedin_user_id', 'page_id') and hasattr(existing_user, key):
                    setattr(existing_user, key, value)
            await self.db.commit()
            await self.db.refresh(existing_user)
            return existing_user
        else:
            # Create new user
            user_data['page_id'] = page_id
            db_user = self.model(**user_data)
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            return db_user
    
    async def upsert_batch(self, users_data: List[Dict[str, Any]], page_id: int) -> List[SocialMediaUser]:
        """Upsert multiple users in batch"""
        upserted_users = []
        for user_data in users_data:
            try:
                user = await self.upsert(user_data, page_id)
                upserted_users.append(user)
            except IntegrityError:
                await self.db.rollback()
                # Retry once after rollback
                try:
                    user = await self.upsert(user_data, page_id)
                    upserted_users.append(user)
                except Exception as e:
                    await self.db.rollback()
                    continue
            except Exception as e:
                await self.db.rollback()
                continue
        
        return upserted_users
