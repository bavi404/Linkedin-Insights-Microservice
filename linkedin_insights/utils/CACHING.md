# Redis Caching

Redis caching implementation for LinkedIn Insights microservice with decorator-based approach and automatic cache invalidation.

## Features

✅ **5-minute TTL**: Page responses cached for 5 minutes by default  
✅ **Cache Invalidation**: Automatic cache invalidation on page updates  
✅ **Decorator-based**: Clean, reusable caching decorators  
✅ **Graceful Degradation**: Works without Redis (caching disabled)  
✅ **Pattern-based Invalidation**: Invalidate related cache keys using patterns  

## Configuration

### Environment Variables

Add to your `.env` file:

```env
# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0
# OR use individual components:
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password  # Optional
REDIS_CACHE_TTL=300  # 5 minutes in seconds
```

### Redis Connection

The application supports two connection methods:

1. **REDIS_URL**: Full connection string
   ```
   REDIS_URL=redis://localhost:6379/0
   REDIS_URL=redis://:password@localhost:6379/0
   ```

2. **Individual Components**: Host, port, DB, password
   ```
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   REDIS_PASSWORD=optional_password
   ```

## Usage

### Automatic Caching

Page endpoints automatically cache responses:

- `GET /api/v1/pages/{page_id}` - Cached for 5 minutes
- `GET /api/v1/pages` - Cached with filter parameters
- `GET /api/v1/pages/{page_id}/posts` - Cached with pagination
- `GET /api/v1/pages/{page_id}/followers` - Cached with pagination

### Cache Keys

Cache keys follow these patterns:

- `page:{page_id}` - Single page
- `pages:list:{hash}` - Pages list with filters
- `pages:{page_id}:posts:{page}:{page_size}` - Page posts
- `pages:{page_id}:followers:{page}:{page_size}` - Page followers

### Manual Cache Operations

```python
from linkedin_insights.utils.redis_client import get_cache, set_cache, delete_cache
from linkedin_insights.utils.cache import invalidate_page_cache

# Get from cache
cached_value = await get_cache("page:acme-corp")

# Set cache
await set_cache("page:acme-corp", page_data, ttl=300)

# Delete cache
await delete_cache("page:acme-corp")

# Invalidate all page-related cache
await invalidate_page_cache()

# Invalidate specific page cache
await invalidate_page_cache("acme-corp")
```

### Cache Invalidation

Cache is automatically invalidated when:

- Page is updated via `process_scraped_data()`
- New data is scraped and stored

The service layer automatically invalidates cache after updates:

```python
# In linkedin_page_service.py
await invalidate_page_cache(page.page_id)
```

## Decorator-Based Caching

### Using Cache Decorator

```python
from linkedin_insights.utils.cache import cache_response

@cache_response(ttl=300, key_prefix="custom")
async def my_function(param1: str, param2: int):
    # Function implementation
    return result
```

### Using Invalidation Decorator

```python
from linkedin_insights.utils.cache import invalidate_cache

@invalidate_cache("page:*")
async def update_page(page_id: str):
    # Function implementation
    return updated_page
```

## Cache Behavior

### When Redis is Available

- ✅ Responses are cached
- ✅ Cache hits return immediately
- ✅ Cache misses execute function and cache result
- ✅ Updates invalidate related cache

### When Redis is Not Available

- ⚠️ Caching is disabled
- ✅ Application continues to work normally
- ✅ No errors thrown
- ✅ All requests hit the database

## Performance Benefits

- **Reduced Database Load**: Frequently accessed pages served from cache
- **Faster Response Times**: Cache hits return in milliseconds
- **Better Scalability**: Handle more concurrent requests
- **Cost Savings**: Fewer database queries

## Monitoring

Cache operations are logged:

- `INFO`: Cache hits/misses
- `DEBUG`: Cache key operations
- `ERROR`: Cache connection/operation errors

## Best Practices

1. **TTL Configuration**: Adjust `REDIS_CACHE_TTL` based on data freshness requirements
2. **Cache Keys**: Use descriptive prefixes for easy pattern matching
3. **Invalidation**: Always invalidate cache after updates
4. **Error Handling**: Cache failures should not break the application
5. **Monitoring**: Monitor cache hit rates for optimization

## Example Flow

```
1. GET /api/v1/pages/acme-corp
   → Check cache (miss)
   → Query database
   → Cache result (5 min TTL)
   → Return response

2. GET /api/v1/pages/acme-corp (within 5 min)
   → Check cache (hit)
   → Return cached response

3. POST /api/v1/scraper/scrape (updates acme-corp)
   → Process data
   → Invalidate cache (page:acme-corp, pages:acme-corp:*)
   → Store in database

4. GET /api/v1/pages/acme-corp (after update)
   → Check cache (miss - invalidated)
   → Query database
   → Cache new result
   → Return response
```

## Troubleshooting

### Cache Not Working

1. Check Redis connection:
   ```python
   from linkedin_insights.utils.redis_client import get_redis_client
   client = await get_redis_client()
   if client is None:
       print("Redis not connected")
   ```

2. Check Redis logs for connection errors

3. Verify environment variables are set correctly

### Cache Not Invalidating

1. Check that `invalidate_page_cache()` is called after updates
2. Verify cache key patterns match
3. Check Redis logs for invalidation operations

## Testing

To test caching:

1. Make a request to an endpoint
2. Check Redis for cached key: `redis-cli KEYS "page:*"`
3. Make the same request again (should be faster)
4. Update the data
5. Make the request again (should fetch fresh data)

