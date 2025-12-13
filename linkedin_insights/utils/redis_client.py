"""
Redis client utility
Async Redis connection and operations
"""
import logging
import json
from typing import Optional, Any
import redis.asyncio as aioredis
from redis.asyncio import Redis

from linkedin_insights.utils.config import settings

logger = logging.getLogger(__name__)

# Global Redis client instance
_redis_client: Optional[Redis] = None


async def get_redis_client() -> Optional[Redis]:
    """
    Get or create Redis client instance
    
    Returns:
        Redis client or None if Redis is not configured
    """
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    # Check if Redis is configured
    if not settings.REDIS_URL and not settings.REDIS_HOST:
        logger.warning("Redis not configured. Caching will be disabled.")
        return None
    
    try:
        # Use REDIS_URL if provided, otherwise construct from components
        if settings.REDIS_URL:
            redis_url = settings.REDIS_URL
        else:
            redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            if settings.REDIS_PASSWORD:
                redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        
        _redis_client = aioredis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        
        # Test connection
        await _redis_client.ping()
        logger.info("Redis client connected successfully")
        
        return _redis_client
    
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        _redis_client = None
        return None


async def close_redis_client():
    """Close Redis client connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis client closed")


async def get_cache(key: str) -> Optional[Any]:
    """
    Get value from cache
    
    Args:
        key: Cache key
    
    Returns:
        Cached value or None if not found
    """
    client = await get_redis_client()
    if not client:
        return None
    
    try:
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Error getting cache key {key}: {str(e)}")
        return None


async def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Set value in cache
    
    Args:
        key: Cache key
        value: Value to cache (must be JSON serializable)
        ttl: Time to live in seconds (defaults to REDIS_CACHE_TTL)
    
    Returns:
        True if successful, False otherwise
    """
    client = await get_redis_client()
    if not client:
        return False
    
    try:
        ttl = ttl or settings.REDIS_CACHE_TTL
        serialized_value = json.dumps(value, default=str)
        await client.setex(key, ttl, serialized_value)
        return True
    except Exception as e:
        logger.error(f"Error setting cache key {key}: {str(e)}")
        return False


async def delete_cache(key: str) -> bool:
    """
    Delete key from cache
    
    Args:
        key: Cache key to delete
    
    Returns:
        True if successful, False otherwise
    """
    client = await get_redis_client()
    if not client:
        return False
    
    try:
        await client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Error deleting cache key {key}: {str(e)}")
        return False


async def delete_cache_pattern(pattern: str) -> int:
    """
    Delete all keys matching pattern
    
    Args:
        pattern: Redis key pattern (e.g., "page:*")
    
    Returns:
        Number of keys deleted
    """
    client = await get_redis_client()
    if not client:
        return 0
    
    try:
        keys = []
        async for key in client.scan_iter(match=pattern):
            keys.append(key)
        
        if keys:
            return await client.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Error deleting cache pattern {pattern}: {str(e)}")
        return 0


async def clear_cache() -> bool:
    """
    Clear all cache
    
    Returns:
        True if successful, False otherwise
    """
    client = await get_redis_client()
    if not client:
        return False
    
    try:
        await client.flushdb()
        return True
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return False

