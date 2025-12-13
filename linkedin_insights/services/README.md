# LinkedIn Page Service

Service layer for processing and persisting scraped LinkedIn page data following SOLID principles and repository pattern.

## Architecture

### Repository Pattern
- **LinkedInPageRepository**: Handles page CRUD operations with upsert support
- **PostRepository**: Handles post operations with batch upsert
- **CommentRepository**: Handles comment operations with batch upsert
- **SocialMediaUserRepository**: Handles employee/user operations with batch upsert

### Service Layer
- **LinkedInPageService**: Orchestrates data processing and persistence
  - Processes scraped data
  - Maintains relationships
  - Uses transactions for data consistency
  - Prevents duplicates using unique constraints

## Features

✅ **Upsert Operations**: Creates or updates records based on unique identifiers
✅ **Transaction Management**: Ensures data consistency with rollback on errors
✅ **Duplicate Prevention**: Uses unique constraints (page_id, post_id, comment_id, linkedin_user_id+page_id)
✅ **Relationship Maintenance**: Automatically links posts, comments, and employees to pages
✅ **Error Handling**: Graceful error handling with detailed logging
✅ **Batch Processing**: Efficient batch upsert for posts, comments, and employees

## Usage

### Basic Usage

```python
from sqlalchemy.orm import Session
from linkedin_insights.services.linkedin_page_service import LinkedInPageService
from linkedin_insights.scraper.page_scraper import LinkedInPageScraper

# Initialize service with database session
service = LinkedInPageService(db_session)

# Scrape data (async)
scraper = LinkedInPageScraper()
scraped_data = await scraper.scrape_page("acme-corp")

# Process and persist scraped data
result = service.process_scraped_data(scraped_data)

if result['success']:
    print(f"Processed page ID: {result['page_id']}")
    print(f"Posts processed: {result['posts_processed']}")
    print(f"Employees processed: {result['employees_processed']}")
else:
    print(f"Error: {result['error']}")
```

### Get Page with Relations

```python
# Get page by LinkedIn page_id
page = service.get_page_by_page_id("acme-corp")

# Get page with all related data
page_data = service.get_page_with_relations("acme-corp")
if page_data:
    print(f"Page: {page_data['page'].name}")
    print(f"Posts: {len(page_data['posts'])}")
    print(f"Employees: {len(page_data['employees'])}")
```

## Unique Constraints

The service prevents duplicates using these unique constraints:

- **LinkedInPage**: `page_id` (unique)
- **Post**: `post_id` (unique)
- **Comment**: `comment_id` (unique)
- **SocialMediaUser**: `(linkedin_user_id, page_id)` (unique combination)

## Transaction Handling

The service uses database transactions to ensure data consistency:

- All operations within `process_scraped_data()` are part of a single transaction
- On success: All changes are committed
- On error: All changes are rolled back
- Individual repository operations also handle their own commits with retry logic

## Error Handling

The service handles various error scenarios:

- **IntegrityError**: Duplicate key violations (handled gracefully)
- **SQLAlchemyError**: Database connection/query errors
- **ValueError**: Missing required data
- **General Exceptions**: Unexpected errors with full logging

## Response Format

### Success Response
```python
{
    'success': True,
    'page_id': 123,
    'page_page_id': 'acme-corp',
    'posts_processed': 20,
    'employees_processed': 15,
    'processed_at': '2024-01-15T12:00:00'
}
```

### Error Response
```python
{
    'success': False,
    'error': 'Error message',
    'page_id': None
}
```

## SOLID Principles

1. **Single Responsibility**: Each repository handles one model, service orchestrates
2. **Open/Closed**: Extensible through inheritance and composition
3. **Liskov Substitution**: Repositories can be substituted via base class
4. **Interface Segregation**: Focused interfaces for each repository
5. **Dependency Inversion**: Service depends on repository abstractions

