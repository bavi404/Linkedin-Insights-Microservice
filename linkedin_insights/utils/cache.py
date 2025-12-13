"""
Caching decorators and utilities
Decorator-based caching for FastAPI endpoints
"""
import functools
import hashlib
import json
import logging
from typing import Callable, Any, Optional, TypeVar, ParamSpec
from fastapi import Request

from linkedin_insights.utils.redis_client import get_cache, set_cache, delete_cache
from linkedin_insights.utils.config import settings

logger = logging.getLogger(__name__)

P = ParamSpec('P')
R = TypeVar('R')


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate cache key from prefix and arguments
    
    Args:
        prefix: Cache key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Cache key string
    """
    # Create a hash of the arguments
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_str.encode()).hexdigest()
    return f"{prefix}:{key_hash}"


def cache_response(
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None,
    include_request: bool = False
):
    """
    Decorator to cache async function responses
    
    Args:
        ttl: Time to live in seconds (defaults to REDIS_CACHE_TTL)
        key_prefix: Cache key prefix (defaults to function name)
        include_request: Whether to include request in cache key (for FastAPI endpoints)
    
    Usage:
        ```python
        @cache_response(ttl=300, key_prefix="page")
        async def get_page(page_id: str):
            # Function implementation
            return page_data
        ```
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            
            # Extract request if present (for FastAPI endpoints)
            request = None
            if include_request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                if not request:
                    request = kwargs.get('request')
            
            # Generate cache key
            cache_key = generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = await get_cache(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value
            
            # Cache miss - execute function
            logger.debug(f"Cache miss for key: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache_ttl = ttl or settings.REDIS_CACHE_TTL
            await set_cache(cache_key, result, cache_ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_pattern: str):
    """
    Decorator to invalidate cache after function execution
    
    Args:
        key_pattern: Redis key pattern to invalidate (e.g., "page:*")
    
    Usage:
        ```python
        @invalidate_cache("page:*")
        async def update_page(page_id: str):
            # Function implementation
            return updated_page
        ```
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Execute function
            result = await func(*args, **kwargs)
            
            # Invalidate cache
            from linkedin_insights.utils.redis_client import delete_cache_pattern
            deleted_count = await delete_cache_pattern(key_pattern)
            if deleted_count > 0:
                logger.info(f"Invalidated {deleted_count} cache keys matching pattern: {key_pattern}")
            
            return result
        
        return wrapper
    return decorator


async def invalidate_page_cache(page_id: Optional[str] = None):
    """
    Invalidate page-related cache
    
    Args:
        page_id: Specific page_id to invalidate, or None to invalidate all pages
    """
    from linkedin_insights.utils.redis_client import delete_cache_pattern, delete_cache
    
    if page_id:
        # Invalidate specific page cache
        patterns = [
            f"page:{page_id}",
            f"pages:{page_id}:*",
            f"page:{page_id}:*"
        ]
        for pattern in patterns:
            await delete_cache_pattern(pattern)
        logger.info(f"Invalidated cache for page: {page_id}")
    else:
        # Invalidate all page cache
        await delete_cache_pattern("page:*")
        await delete_cache_pattern("pages:*")
        logger.info("Invalidated all page cache")


def get_cache_key_for_page(page_id: str) -> str:
    """Get cache key for a specific page"""
    return f"page:{page_id}"


def get_cache_key_for_pages_list(filters: dict) -> str:
    """Get cache key for pages list with filters"""
    return generate_cache_key("pages:list", **filters)


def get_cache_key_for_page_posts(page_id: str, page: int, page_size: int) -> str:
    """Get cache key for page posts"""
    return f"pages:{page_id}:posts:{page}:{page_size}"


def get_cache_key_for_page_followers(page_id: str, page: int, page_size: int) -> str:
    """Get cache key for page followers"""
    return f"pages:{page_id}:followers:{page}:{page_size}"

