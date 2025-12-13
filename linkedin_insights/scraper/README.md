# LinkedIn Page Scraper

Playwright-based scraper for LinkedIn company pages.

## Features

- Scrapes LinkedIn page information (name, description, followers, etc.)
- Fetches latest 20 posts with engagement metrics
- Extracts comments for each post (5-10 comments)
- Scrapes employee/people information
- Headless browser mode
- Retry logic with configurable attempts
- Timeout handling
- Graceful error handling

## Usage

### Async Usage (Recommended for FastAPI)

```python
from linkedin_insights.scraper.page_scraper import LinkedInPageScraper

async def scrape_page():
    scraper = LinkedInPageScraper()
    result = await scraper.scrape_page("acme-corp")
    return result
```

### Sync Usage

```python
from linkedin_insights.scraper.scraper_service import ScraperService

scraper = ScraperService()
result = scraper.scrape_linkedin_page("acme-corp")
```

## Configuration

Set these environment variables:

```env
SCRAPER_TIMEOUT=30
SCRAPER_RETRY_ATTEMPTS=3
SCRAPER_HEADLESS=True
SCRAPER_PAGE_LOAD_TIMEOUT=60000
SCRAPER_NAVIGATION_TIMEOUT=30000
```

## Response Format

```python
{
    "page_info": {
        "page_id": "acme-corp",
        "name": "Acme Corporation",
        "url": "https://www.linkedin.com/company/acme-corp",
        "linkedin_internal_id": "123456",
        "profile_image_url": "https://...",
        "description": "Company description...",
        "website": "https://acme.com",
        "industry": "Technology",
        "total_followers": 10000,
        "head_count": 500,
        "specialities": "Software, AI, Cloud"
    },
    "posts": [
        {
            "post_id": "urn:li:activity:123",
            "content": "Post content...",
            "like_count": 150,
            "comment_count": 20,
            "posted_at": "2024-01-15T10:00:00",
            "comments": [
                {
                    "comment_id": "comment_123",
                    "author_name": "John Doe",
                    "content": "Great post!",
                    "created_at": "2024-01-15T11:00:00"
                }
            ]
        }
    ],
    "employees": [
        {
            "linkedin_user_id": "john-doe",
            "name": "John Doe",
            "title": "Software Engineer",
            "profile_url": "https://www.linkedin.com/in/john-doe"
        }
    ],
    "scraped_at": "2024-01-15T12:00:00"
}
```

## Error Handling

If scraping fails, the response will include:

```python
{
    "error": True,
    "error_message": "Page not found or inaccessible",
    "page_info": None,
    "posts": [],
    "employees": [],
    "scraped_at": "2024-01-15T12:00:00"
}
```

## Installation

After installing requirements, install Playwright browsers:

```bash
playwright install chromium
```

