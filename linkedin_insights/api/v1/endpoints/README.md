# LinkedIn Pages API Endpoints

FastAPI routes for LinkedIn company pages with dependency injection, proper HTTP status codes, and clean response models.

## Endpoints

### 1. GET `/api/v1/pages/{page_id}`

Get a LinkedIn page by page_id.

**Behavior:**
- If page exists in DB → returns from database
- If not → scrapes LinkedIn, stores in DB, returns response

**Parameters:**
- `page_id` (path): LinkedIn page ID (last part of company URL)

**Response:** `LinkedInPageResponse`
- Status: `200 OK` (page found or scraped successfully)
- Status: `404 Not Found` (page not found on LinkedIn)
- Status: `500 Internal Server Error` (scraping/processing error)

**Example:**
```bash
GET /api/v1/pages/acme-corp
```

### 2. GET `/api/v1/pages`

Get list of LinkedIn pages with filtering and pagination.

**Query Parameters:**
- `page` (int, default=1, min=1): Page number
- `page_size` (int, default=20, min=1, max=100): Items per page
- `follower_count_min` (int, optional, min=0): Minimum follower count
- `follower_count_max` (int, optional, min=0): Maximum follower count
- `industry` (string, optional): Filter by industry (partial match)
- `page_name` (string, optional): Filter by page name (partial match, case-insensitive)

**Response:** `PaginatedLinkedInPageResponse`
- Status: `200 OK`

**Example:**
```bash
GET /api/v1/pages?page=1&page_size=20&follower_count_min=1000&industry=Technology
GET /api/v1/pages?page_name=acme&follower_count_max=50000
```

### 3. GET `/api/v1/pages/{page_id}/posts`

Get posts for a LinkedIn page with pagination.

**Parameters:**
- `page_id` (path): LinkedIn page ID
- `page` (int, default=1, min=1): Page number
- `page_size` (int, default=15, min=1, max=50): Items per page (recommended 10-15)

**Response:** `PaginatedPostResponse`
- Status: `200 OK`
- Status: `404 Not Found` (page not found)

**Example:**
```bash
GET /api/v1/pages/acme-corp/posts?page=1&page_size=15
```

### 4. GET `/api/v1/pages/{page_id}/followers`

Get employees/followers for a LinkedIn page with pagination.

**Parameters:**
- `page_id` (path): LinkedIn page ID
- `page` (int, default=1, min=1): Page number
- `page_size` (int, default=20, min=1, max=100): Items per page

**Response:** `PaginatedSocialMediaUserResponse`
- Status: `200 OK`
- Status: `404 Not Found` (page not found)

**Example:**
```bash
GET /api/v1/pages/acme-corp/followers?page=1&page_size=20
```

## Response Models

### Paginated Response Structure

All paginated endpoints return:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5,
  "has_next": true,
  "has_previous": false
}
```

## Features

✅ **Dependency Injection**: Database sessions injected via FastAPI dependencies
✅ **Proper HTTP Status Codes**: 200, 404, 500 as appropriate
✅ **Clean Response Models**: Pydantic schemas for validation and serialization
✅ **Pagination Support**: Consistent pagination across list endpoints
✅ **Filtering**: Multiple filter options for pages endpoint
✅ **Error Handling**: Comprehensive error handling with detailed messages
✅ **Async Support**: Async endpoint for scraping operations

## Error Responses

All endpoints return consistent error format:
```json
{
  "detail": "Error message description"
}
```

## Usage Examples

### Get a page (with auto-scraping)
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/api/v1/pages/acme-corp")
    page_data = response.json()
```

### List pages with filters
```python
params = {
    "page": 1,
    "page_size": 20,
    "follower_count_min": 1000,
    "industry": "Technology"
}
response = await client.get("http://localhost:8000/api/v1/pages", params=params)
```

### Get page posts
```python
response = await client.get(
    "http://localhost:8000/api/v1/pages/acme-corp/posts",
    params={"page": 1, "page_size": 15}
)
```

