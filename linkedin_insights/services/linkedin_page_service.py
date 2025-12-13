"""
LinkedIn Page Service
Async service layer for processing and persisting scraped LinkedIn page data
Follows SOLID principles and repository pattern
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from linkedin_insights.db.repositories import (
    LinkedInPageRepository,
    PostRepository,
    CommentRepository,
    SocialMediaUserRepository,
)
from linkedin_insights.models.linkedin import (
    LinkedInPage,
    Post,
    Comment,
    SocialMediaUser,
)
from linkedin_insights.services.ai_summary_service import AISummaryService

logger = logging.getLogger(__name__)


class LinkedInPageService:
    """
    Async service for processing scraped LinkedIn page data
    Handles upsert operations with transactions and duplicate prevention
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.page_repo = LinkedInPageRepository(LinkedInPage, db)
        self.post_repo = PostRepository(Post, db)
        self.comment_repo = CommentRepository(Comment, db)
        self.user_repo = SocialMediaUserRepository(SocialMediaUser, db)
        # Optional AI summary service
        self.ai_summary_service = AISummaryService()
    
    async def process_scraped_data(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and persist scraped LinkedIn page data
        
        Args:
            scraped_data: Dictionary from scraper with page_info, posts, employees
        
        Returns:
            Dictionary with processing results
        """
        if scraped_data.get('error'):
            logger.warning(f"Scraped data contains error: {scraped_data.get('error_message')}")
            return {
                'success': False,
                'error': scraped_data.get('error_message'),
                'page_id': None
            }
        
        try:
            # Upsert page information
            page_info = scraped_data.get('page_info', {})
            if not page_info:
                raise ValueError("page_info is required in scraped_data")
            
            page = await self._upsert_page(page_info)
            
            # Process posts and comments
            posts_data = scraped_data.get('posts', [])
            posts_processed = await self._process_posts(posts_data, page.id)
            
            # Process employees
            employees_data = scraped_data.get('employees', [])
            employees_processed = await self._process_employees(employees_data, page.id)
            
            # Final commit for any remaining changes
            await self.db.commit()
            
            logger.info(
                f"Successfully processed page {page.page_id}: "
                f"{len(posts_processed)} posts, {len(employees_processed)} employees"
            )
            
            return {
                'success': True,
                'page_id': page.id,
                'page_page_id': page.page_id,
                'posts_processed': len(posts_processed),
                'employees_processed': len(employees_processed),
                'processed_at': datetime.utcnow().isoformat()
            }
        
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error processing scraped data: {str(e)}")
            return {
                'success': False,
                'error': f"Database integrity error: {str(e)}",
                'page_id': None
            }
        
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error processing scraped data: {str(e)}")
            return {
                'success': False,
                'error': f"Database error: {str(e)}",
                'page_id': None
            }
        
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error processing scraped data: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'page_id': None
            }
    
    async def _upsert_page(self, page_info: Dict[str, Any]) -> LinkedInPage:
        """
        Upsert page information
        Handles duplicate prevention using unique constraints
        """
        try:
            # Prepare page data
            page_data = {
                'page_id': page_info.get('page_id'),
                'name': page_info.get('name', 'Unknown'),
                'url': page_info.get('url'),
                'linkedin_internal_id': page_info.get('linkedin_internal_id'),
                'description': page_info.get('description'),
                'website': page_info.get('website'),
                'industry': page_info.get('industry'),
                'total_followers': page_info.get('total_followers'),
                'head_count': page_info.get('head_count'),
                'specialities': page_info.get('specialities'),
                'profile_image_url': page_info.get('profile_image_url'),
            }
            
            # Remove None values to avoid overwriting with None
            page_data = {k: v for k, v in page_data.items() if v is not None}
            
            page = await self.page_repo.upsert(page_data)
            logger.debug(f"Upserted page: {page.page_id} (ID: {page.id})")
            return page
        
        except IntegrityError as e:
            await self.db.rollback()
            logger.error(f"Integrity error upserting page: {str(e)}")
            raise
    
    async def _process_posts(self, posts_data: List[Dict[str, Any]], page_id: int) -> List[Any]:
        """
        Process posts and their comments
        Uses batch upsert for efficiency
        """
        if not posts_data:
            return []
        
        processed_posts = []
        
        for post_data in posts_data:
            try:
                # Extract comments before processing post
                comments_data = post_data.pop('comments', [])
                
                # Prepare post data
                post_dict = {
                    'post_id': post_data.get('post_id'),
                    'content': post_data.get('content'),
                    'like_count': post_data.get('like_count', 0),
                    'comment_count': post_data.get('comment_count', 0),
                }
                
                # Parse posted_at timestamp
                posted_at = post_data.get('posted_at')
                if posted_at:
                    if isinstance(posted_at, str):
                        try:
                            # Try parsing ISO format
                            posted_at = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
                        except:
                            try:
                                # Try parsing other formats
                                posted_at = datetime.strptime(posted_at, '%Y-%m-%dT%H:%M:%S')
                            except:
                                posted_at = datetime.utcnow()
                    post_dict['posted_at'] = posted_at
                else:
                    post_dict['posted_at'] = datetime.utcnow()
                
                # Remove None values
                post_dict = {k: v for k, v in post_dict.items() if v is not None}
                
                # Upsert post
                post = await self.post_repo.upsert(post_dict, page_id)
                processed_posts.append(post)
                
                # Process comments for this post
                if comments_data:
                    await self._process_comments(comments_data, post.id)
            
            except IntegrityError as e:
                await self.db.rollback()
                logger.warning(f"Integrity error processing post {post_data.get('post_id')}: {str(e)}")
                # Retry once
                try:
                    post_dict = {
                        'post_id': post_data.get('post_id'),
                        'content': post_data.get('content'),
                        'like_count': post_data.get('like_count', 0),
                        'comment_count': post_data.get('comment_count', 0),
                    }
                    posted_at = post_data.get('posted_at')
                    if posted_at and isinstance(posted_at, str):
                        try:
                            posted_at = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
                        except:
                            posted_at = datetime.utcnow()
                    post_dict['posted_at'] = posted_at or datetime.utcnow()
                    post_dict = {k: v for k, v in post_dict.items() if v is not None}
                    post = await self.post_repo.upsert(post_dict, page_id)
                    processed_posts.append(post)
                    if comments_data:
                        await self._process_comments(comments_data, post.id)
                except Exception as retry_e:
                    logger.error(f"Retry failed for post {post_data.get('post_id')}: {str(retry_e)}")
                    continue
            
            except Exception as e:
                logger.warning(f"Error processing post {post_data.get('post_id')}: {str(e)}")
                continue
        
        return processed_posts
    
    async def _process_comments(self, comments_data: List[Dict[str, Any]], post_id: int) -> List[Any]:
        """
        Process comments for a post
        Uses batch upsert for efficiency
        """
        if not comments_data:
            return []
        
        processed_comments = []
        
        for comment_data in comments_data:
            try:
                # Prepare comment data
                comment_dict = {
                    'comment_id': comment_data.get('comment_id'),
                    'author_name': comment_data.get('author_name'),
                    'content': comment_data.get('content'),
                }
                
                # Parse created_at timestamp
                created_at = comment_data.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except:
                            created_at = datetime.utcnow()
                    comment_dict['created_at'] = created_at
                else:
                    comment_dict['created_at'] = datetime.utcnow()
                
                # Remove None values
                comment_dict = {k: v for k, v in comment_dict.items() if v is not None}
                
                # Upsert comment
                comment = await self.comment_repo.upsert(comment_dict, post_id)
                processed_comments.append(comment)
            
            except IntegrityError as e:
                await self.db.rollback()
                logger.warning(f"Integrity error processing comment {comment_data.get('comment_id')}: {str(e)}")
                # Retry once
                try:
                    comment_dict = {
                        'comment_id': comment_data.get('comment_id'),
                        'author_name': comment_data.get('author_name'),
                        'content': comment_data.get('content'),
                    }
                    created_at = comment_data.get('created_at')
                    if created_at and isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except:
                            created_at = datetime.utcnow()
                    comment_dict['created_at'] = created_at or datetime.utcnow()
                    comment_dict = {k: v for k, v in comment_dict.items() if v is not None}
                    comment = await self.comment_repo.upsert(comment_dict, post_id)
                    processed_comments.append(comment)
                except Exception as retry_e:
                    logger.error(f"Retry failed for comment {comment_data.get('comment_id')}: {str(retry_e)}")
                    continue
            
            except Exception as e:
                logger.warning(f"Error processing comment {comment_data.get('comment_id')}: {str(e)}")
                continue
        
        return processed_comments
    
    async def _process_employees(self, employees_data: List[Dict[str, Any]], page_id: int) -> List[Any]:
        """
        Process employees/users
        Uses batch upsert for efficiency
        """
        if not employees_data:
            return []
        
        processed_employees = []
        
        for employee_data in employees_data:
            try:
                # Prepare user data
                user_dict = {
                    'linkedin_user_id': employee_data.get('linkedin_user_id'),
                    'name': employee_data.get('name'),
                    'title': employee_data.get('title'),
                    'profile_url': employee_data.get('profile_url'),
                }
                
                # Remove None values
                user_dict = {k: v for k, v in user_dict.items() if v is not None}
                
                # Upsert user (unique constraint on linkedin_user_id + page_id)
                user = await self.user_repo.upsert(user_dict, page_id)
                processed_employees.append(user)
            
            except IntegrityError as e:
                await self.db.rollback()
                logger.warning(f"Integrity error processing employee {employee_data.get('linkedin_user_id')}: {str(e)}")
                # Retry once
                try:
                    user_dict = {
                        'linkedin_user_id': employee_data.get('linkedin_user_id'),
                        'name': employee_data.get('name'),
                        'title': employee_data.get('title'),
                        'profile_url': employee_data.get('profile_url'),
                    }
                    user_dict = {k: v for k, v in user_dict.items() if v is not None}
                    user = await self.user_repo.upsert(user_dict, page_id)
                    processed_employees.append(user)
                except Exception as retry_e:
                    logger.error(f"Retry failed for employee {employee_data.get('linkedin_user_id')}: {str(retry_e)}")
                    continue
            
            except Exception as e:
                logger.warning(f"Error processing employee {employee_data.get('linkedin_user_id')}: {str(e)}")
                continue
        
        return processed_employees
    
    async def get_page_by_page_id(self, page_id: str) -> Optional[LinkedInPage]:
        """Get page by LinkedIn page_id"""
        return await self.page_repo.get_by_page_id(page_id)
    
    async def get_page_with_relations(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Get page with all related data"""
        page = await self.page_repo.get_by_page_id(page_id)
        if not page:
            return None
        
        # Load related data
        posts = await self.post_repo.get_by_page_id(page.id)
        employees = await self.user_repo.get_by_page_id(page.id)
        
        return {
            'page': page,
            'posts': posts,
            'employees': employees
        }
    
    async def generate_ai_summary(self, page_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate AI summary for a LinkedIn page
        
        Args:
            page_id: LinkedIn page_id
        
        Returns:
            AI summary dictionary or None if service is disabled
        """
        page = await self.page_repo.get_by_page_id(page_id)
        if not page:
            return None
        
        # Get posts for engagement metrics
        posts = await self.post_repo.get_by_page_id(page.id, limit=100)
        
        # Calculate engagement metrics
        total_posts = len(posts)
        total_likes = sum(post.like_count for post in posts) if posts else 0
        total_comments = sum(post.comment_count for post in posts) if posts else 0
        avg_likes = total_likes / total_posts if total_posts > 0 else 0
        avg_comments = total_comments / total_posts if total_posts > 0 else 0
        
        # Calculate engagement rate (simplified: (avg_likes + avg_comments) / followers * 100)
        engagement_rate = None
        if page.total_followers and page.total_followers > 0:
            engagement_rate = ((avg_likes + avg_comments) / page.total_followers) * 100
        
        # Prepare page stats
        page_stats = {
            'name': page.name,
            'industry': page.industry,
            'total_followers': page.total_followers,
            'head_count': page.head_count,
            'description': page.description,
            'total_posts': total_posts,
            'avg_likes': avg_likes,
            'avg_comments': avg_comments,
            'engagement_rate': engagement_rate,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Generate AI summary
        return self.ai_summary_service.generate_summary(page_stats)
