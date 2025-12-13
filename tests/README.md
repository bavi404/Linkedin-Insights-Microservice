# Test Suite

Comprehensive pytest-based test suite for LinkedIn Insights Microservice.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_api/
│   ├── test_insights.py          # Insight endpoint tests
│   ├── test_pages.py             # Page endpoint tests
│   └── test_scraper.py           # Scraper endpoint tests
├── test_services/
│   ├── test_insight_service.py   # Insight service tests
│   └── test_scraper_service.py   # Scraper service tests (mocked)
├── test_utils/
│   └── test_pagination.py        # Pagination utility tests
└── test_scraper/
    └── test_linkedin_scraper.py  # Scraper unit tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=linkedin_insights --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_api/test_pages.py
```

### Run specific test class
```bash
pytest tests/test_api/test_pages.py::TestGetPage
```

### Run specific test
```bash
pytest tests/test_api/test_pages.py::TestGetPage::test_get_page_from_db
```

### Run with verbose output
```bash
pytest -v
```

## Test Coverage

The test suite covers:

### API Endpoints
- ✅ Page fetch endpoint (GET /pages/{page_id})
- ✅ Filtered page search (GET /pages with filters)
- ✅ Page posts endpoint (GET /pages/{page_id}/posts)
- ✅ Page followers endpoint (GET /pages/{page_id}/followers)
- ✅ Pagination logic

### Services
- ✅ Scraper service (mocked Playwright)
- ✅ Page service with database operations

### Utilities
- ✅ Pagination utility functions
- ✅ PaginationParams and PaginationResult classes

## Test Fixtures

### Database Fixtures
- `db_session`: Creates a test database session with SQLite
- `client`: FastAPI TestClient with database dependency override

### Data Fixtures
- `sample_page`: Creates a sample LinkedIn page
- `sample_pages`: Creates multiple sample pages (10 pages)
- `sample_posts`: Creates sample posts for a page

## Mocking

The scraper service tests use mocks to avoid actual web scraping:
- Playwright browser is mocked
- Scraper responses are mocked
- No actual HTTP requests are made

## Database

Tests use SQLite in-memory database:
- Database is created before each test
- Database is dropped after each test
- Each test gets a clean database state

## Example Test

```python
def test_get_page_from_db(client, sample_page):
    """Test getting a page that exists in database"""
    response = client.get(f"/api/v1/pages/{sample_page.page_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["page_id"] == sample_page.page_id
```

## Dependencies

Required packages for testing:
- pytest
- pytest-asyncio
- pytest-cov
- fastapi (for TestClient)
- sqlalchemy (for test database)

All dependencies are listed in `requirements.txt`.

