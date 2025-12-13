# Pagination Utility

Reusable pagination utility for FastAPI endpoints with SQLAlchemy integration.

## Features

- ✅ Accepts `page` and `page_size` parameters
- ✅ Returns `total_count`, `total_pages`, `current_page`
- ✅ Integrates seamlessly with SQLAlchemy queries
- ✅ FastAPI dependency injection support
- ✅ Automatic pagination metadata calculation

## Usage

### Basic Usage

```python
from linkedin_insights.utils.pagination import paginate_query
from sqlalchemy.orm import Session

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    query = db.query(Item)
    result = paginate_query(query, page=1, page_size=20)
    return result.to_dict()
```

### With FastAPI Dependency Injection

```python
from linkedin_insights.utils.pagination import (
    PaginationParams,
    get_pagination_dependency,
    paginate_query
)

@router.get("/items")
def get_items(
    pagination: PaginationParams = Depends(get_pagination_dependency),
    db: Session = Depends(get_db)
):
    query = db.query(Item)
    result = paginate_query(query, pagination.page, pagination.page_size)
    return result.to_dict()
```

### With Ordering

```python
from linkedin_insights.utils.pagination import (
    PaginationParams,
    paginate_query_with_filters
)

@router.get("/posts")
def get_posts(
    pagination: PaginationParams = Depends(get_pagination_dependency),
    db: Session = Depends(get_db)
):
    query = db.query(Post)
    result = paginate_query_with_filters(
        query,
        pagination,
        order_by=Post.created_at.desc()
    )
    return result.to_dict()
```

### With Filters

```python
@router.get("/pages")
def get_pages(
    pagination: PaginationParams = Depends(get_pagination_dependency),
    industry: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LinkedInPage)
    
    # Apply filters
    if industry:
        query = query.filter(LinkedInPage.industry.ilike(f"%{industry}%"))
    
    # Paginate
    result = paginate_query(query, pagination.page, pagination.page_size)
    return result.to_dict()
```

## Response Format

The pagination utility returns a dictionary with:

```python
{
    'items': [...],           # List of items
    'total': 100,             # Total count
    'page': 1,                # Current page
    'page_size': 20,          # Items per page
    'total_pages': 5,         # Total pages
    'has_next': True,         # Has next page
    'has_previous': False     # Has previous page
}
```

## API Reference

### `PaginationParams`

Class for pagination parameters.

**Properties:**
- `page`: Page number (1-indexed)
- `page_size`: Items per page
- `skip`: Calculated skip offset
- `limit`: Same as page_size

### `PaginationResult`

Container for pagination results.

**Properties:**
- `items`: List of paginated items
- `total_count`: Total number of items
- `page`: Current page number
- `page_size`: Items per page
- `total_pages`: Calculated total pages
- `has_next`: Boolean indicating next page exists
- `has_previous`: Boolean indicating previous page exists
- `to_dict()`: Convert to dictionary for API response

### `paginate_query(query, page, page_size)`

Paginate a SQLAlchemy query.

**Parameters:**
- `query`: SQLAlchemy query object
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Returns:** `PaginationResult`

### `paginate_query_with_filters(query, pagination, order_by=None)`

Paginate a SQLAlchemy query with optional ordering.

**Parameters:**
- `query`: SQLAlchemy query object
- `pagination`: `PaginationParams` instance
- `order_by`: Optional column to order by (e.g., `Model.created_at.desc()`)

**Returns:** `PaginationResult`

### `get_pagination_dependency(page, page_size)`

FastAPI dependency for pagination parameters.

**Usage:**
```python
pagination: PaginationParams = Depends(get_pagination_dependency)
```

### `create_pagination_metadata(total_count, page, page_size)`

Create pagination metadata dictionary (without items).

**Returns:** Dictionary with pagination metadata

## Examples

### Example 1: Simple List Endpoint

```python
@router.get("/users", response_model=PaginatedUserResponse)
def get_users(
    pagination: PaginationParams = Depends(get_pagination_dependency),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    result = paginate_query(query, pagination.page, pagination.page_size)
    return result.to_dict()
```

### Example 2: Filtered and Ordered

```python
@router.get("/posts", response_model=PaginatedPostResponse)
def get_posts(
    pagination: PaginationParams = Depends(get_pagination_dependency),
    author_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Post)
    
    if author_id:
        query = query.filter(Post.author_id == author_id)
    
    result = paginate_query_with_filters(
        query,
        pagination,
        order_by=Post.created_at.desc()
    )
    return result.to_dict()
```

### Example 3: Custom Page Size

```python
@router.get("/items")
def get_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),  # Custom max
    db: Session = Depends(get_db)
):
    pagination = PaginationParams(page=page, page_size=page_size)
    query = db.query(Item)
    result = paginate_query(query, pagination.page, pagination.page_size)
    return result.to_dict()
```

## Benefits

1. **Consistency**: Same pagination logic across all endpoints
2. **DRY**: No code duplication
3. **Type Safety**: Type hints and validation
4. **Easy to Use**: Simple API with sensible defaults
5. **Flexible**: Supports custom page sizes and ordering
6. **FastAPI Integration**: Works seamlessly with dependency injection

