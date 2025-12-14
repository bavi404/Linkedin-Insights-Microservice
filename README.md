# LinkedIn Insights Microservice

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-grade, async FastAPI microservice for scraping, storing, and analyzing LinkedIn company page data. Features intelligent caching, AI-powered summaries, and comprehensive API endpoints for accessing LinkedIn insights.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Quick Start](#quick-start)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Scraping Limitations](#scraping-limitations)
- [Bonus Features](#bonus-features)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Contributing](#contributing)

## Project Overview

LinkedIn Insights Microservice is a robust, scalable solution for extracting and managing LinkedIn company page data. It provides:

- **Automated Scraping**: Playwright-based web scraping for LinkedIn company pages
- **Data Persistence**: PostgreSQL database with async SQLAlchemy ORM
- **Intelligent Caching**: Redis-based caching with automatic invalidation
- **AI Summaries**: Optional OpenAI-powered page analysis
- **RESTful API**: Comprehensive FastAPI endpoints with pagination and filtering
- **Production Ready**: Docker support, health checks, and comprehensive testing

### Use Cases

- Competitive intelligence and market research
- Social media analytics and engagement tracking
- Company profile aggregation and analysis
- Lead generation and prospect research
- Content strategy and performance analysis

## Architecture

The application follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Layer (Endpoints)                     │   │
│  │  • Pages, Insights, Scraper, AI Summary                │   │
│  └──────────────────┬────────────────────────────────────┘   │
│                     │                                         │
│  ┌──────────────────▼────────────────────────────────────┐   │
│  │           Service Layer (Business Logic)                │   │
│  │  • LinkedInPageService, InsightService                  │   │
│  │  • ScraperService, AISummaryService                     │   │
│  └──────────────────┬────────────────────────────────────┘   │
│                     │                                         │
│  ┌──────────────────▼────────────────────────────────────┐   │
│  │        Repository Layer (Data Access)                   │   │
│  │  • LinkedInPageRepository, PostRepository              │   │
│  │  • CommentRepository, SocialMediaUserRepository        │   │
│  └──────────────────┬────────────────────────────────────┘   │
│                     │                                         │
│  ┌──────────────────▼────────────────────────────────────┐   │
│  │              Database Layer (SQLAlchemy)                │   │
│  │  • Async SQLAlchemy ORM                                 │   │
│  │  • PostgreSQL / SQLite                                 │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    External Services                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Redis      │  │  Playwright  │  │   OpenAI     │     │
│  │  (Caching)   │  │  (Scraping)  │  │  (AI Summary)│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Request** → FastAPI endpoint receives HTTP request
2. **Cache Check** → Redis checked for cached response (5-minute TTL)
3. **Service Layer** → Business logic processes request
4. **Repository** → Data access layer queries/updates database
5. **Response** → Cached and returned to client

### Key Components

- **API Layer**: FastAPI routes with dependency injection
- **Service Layer**: Business logic and orchestration
- **Repository Layer**: Data access abstraction
- **Database Layer**: Async SQLAlchemy ORM
- **Scraper**: Playwright-based web scraping
- **Cache**: Redis for response caching
- **AI Service**: Optional OpenAI integration

## Tech Stack

### Core Framework
- **FastAPI** 0.104 - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server with production-ready configuration
- **Python** 3.11 - Latest Python features and performance

### Database & ORM
- **PostgreSQL** 15 - Production database
- **SQLAlchemy** 2.0 (async) - Modern async ORM
- **Alembic** - Database migrations
- **asyncpg** - Async PostgreSQL driver
- **aiosqlite** - Async SQLite (for testing)

### Caching
- **Redis** 7 - In-memory data store
- **redis-py** - Python Redis client with async support

### Web Scraping
- **Playwright** - Headless browser automation
- **Chromium** - Browser engine for scraping

### AI & ML (Optional)
- **OpenAI API** - GPT models for AI summaries

### Validation & Configuration
- **Pydantic** 2.5 - Data validation and settings
- **pydantic-settings** - Environment-based configuration

### Testing
- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## Features

### Core Features
- **Async Architecture**: Full async/await support for high concurrency
- **Clean Architecture**: Separation of concerns with repository pattern
- **RESTful API**: Comprehensive endpoints with OpenAPI documentation
- **Data Persistence**: PostgreSQL with async SQLAlchemy
- **Web Scraping**: Playwright-based LinkedIn page scraping
- **Intelligent Caching**: Redis caching with 5-minute TTL
- **Cache Invalidation**: Automatic cache invalidation on updates
- **Pagination**: Reusable pagination utility
- **Filtering**: Advanced filtering for page searches
- **Error Handling**: Comprehensive error handling and logging

### Advanced Features
- **AI Summaries**: Optional OpenAI-powered page analysis
- **Auto-scraping**: Automatic scraping when page not in database
- **Engagement Metrics**: Post likes, comments, and engagement rates
- **Employee Data**: Scrape and store employee information
- **Comments**: Extract and store post comments
- **Relationships**: Proper database relationships and cascades

### Production Features
- **Docker Support**: Multi-stage Dockerfile and docker-compose
- **Health Checks**: Application and service health monitoring
- **Logging**: Structured logging with configurable levels
- **Security**: Non-root containers, environment-based config
- **Performance**: Optimized queries, connection pooling
- **Monitoring**: Health endpoints and metrics

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)
- Redis 7+ (optional, for caching)
- Docker & Docker Compose (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/bavi404/Linkedin-Insights-Microservice.git
cd Linkedin-Insights-Microservice

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

**Required Environment Variables:**

```env
# REQUIRED: Database connection
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/linkedin_insights
```

**Optional Environment Variables:**

```env
# Redis (for caching - optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=                    # Optional password
REDIS_CACHE_TTL=300                # Cache TTL in seconds (default: 5 minutes)

# Scraper configuration (optional, has defaults)
SCRAPER_TIMEOUT=30
SCRAPER_RETRY_ATTEMPTS=3
SCRAPER_HEADLESS=true
SCRAPER_PAGE_LOAD_TIMEOUT=60000
SCRAPER_NAVIGATION_TIMEOUT=30000

# AI Summary (optional - requires OpenAI API key)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=300

# Application settings (optional, has defaults)
APP_NAME=linkedin_insights
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["*"]
```

**Quick Setup:**

1. **Minimum (Database only):**
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/linkedin_insights
   ```

2. **With Caching:**
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/linkedin_insights
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

3. **Full Setup**
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/linkedin_insights
   REDIS_HOST=localhost
   REDIS_PORT=6379
   OPENAI_API_KEY=sk-your-key-here
   ```

### Run Application

```bash
# Run migrations
alembic upgrade head

# Start server
uvicorn linkedin_insights.main:app --reload
```

Visit: http://localhost:8000/docs for API documentation

## Setup Instructions

### Local Development Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Setup Database**
   ```bash
   # Create PostgreSQL database
   createdb linkedin_insights
   
   # Run migrations
   alembic upgrade head
   ```

3. **Setup Redis** (Optional)
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:7-alpine
   
   # Or install locally
   # macOS: brew install redis
   # Ubuntu: sudo apt-get install redis-server
   ```

4. **Configure Environment**
   ```bash
   cp .docker.env.example .env
   # Edit .env with your settings
   ```

5. **Run Application**
   ```bash
   uvicorn linkedin_insights.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Setup

See [DOCKER.md](DOCKER.md) for detailed Docker deployment instructions.

```bash
# Quick start with Docker
docker-compose up -d

# Run migrations
docker-compose exec app alembic upgrade head

# View logs
docker-compose logs -f app
```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### Pages

##### `GET /pages/{page_id}`
Get a LinkedIn page by page_id. Automatically scrapes if not in database.

**Parameters:**
- `page_id` (path): LinkedIn page ID (e.g., "acme-corp")

**Response:** `200 OK`
```json
{
  "id": 1,
  "page_id": "acme-corp",
  "name": "Acme Corporation",
  "url": "https://www.linkedin.com/company/acme-corp",
  "total_followers": 10000,
  "industry": "Technology",
  "description": "Leading technology company...",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

##### `GET /pages`
Get list of LinkedIn pages with filtering and pagination.

**Query Parameters:**
- `page` (int, default=1): Page number
- `page_size` (int, default=20, max=100): Items per page
- `follower_count_min` (int, optional): Minimum follower count
- `follower_count_max` (int, optional): Maximum follower count
- `industry` (string, optional): Filter by industry (partial match)
- `page_name` (string, optional): Filter by page name (partial match)

**Response:** `200 OK`
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

##### `GET /pages/{page_id}/posts`
Get posts for a LinkedIn page with pagination.

**Query Parameters:**
- `page` (int, default=1): Page number
- `page_size` (int, default=15, max=50): Items per page

**Response:** `200 OK` - Paginated posts with comments

##### `GET /pages/{page_id}/followers`
Get employees/followers for a LinkedIn page with pagination.

**Query Parameters:**
- `page` (int, default=1): Page number
- `page_size` (int, default=20, max=100): Items per page

**Response:** `200 OK` - Paginated users/employees

#### AI Summary (Optional)

##### `GET /pages/{page_id}/summary`
Generate AI-powered summary for a LinkedIn page.

**Requirements:** OpenAI API key configured

**Response:** `200 OK`
```json
{
  "summary": "Acme Corporation is a large enterprise...",
  "page_type": "Enterprise",
  "audience": "Large",
  "engagement": "High",
  "generated_at": "2024-01-15T12:00:00Z"
}
```

##### `POST /summary/generate`
Generate AI summary from provided page statistics.

**Request Body:**
```json
{
  "name": "Tech Startup Inc",
  "industry": "Technology",
  "total_followers": 5000,
  "head_count": 50,
  "total_posts": 20,
  "avg_likes": 150,
  "avg_comments": 25
}
```

#### Scraper

##### `POST /scraper/scrape`
Scrape LinkedIn profile/page and create insight.

**Request Body:**
```json
{
  "profile_url": "https://www.linkedin.com/company/acme-corp"
}
```

### Response Codes

- `200 OK` - Successful request
- `201 Created` - Resource created
- `202 Accepted` - Request accepted (async processing)
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service unavailable (e.g., AI service disabled)

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

## ⚠️ Scraping Limitations

### Technical Limitations

1. **Rate Limiting**: LinkedIn may rate limit or block excessive requests
   - **Solution**: Implement request throttling and respect robots.txt

2. **Dynamic Content**: LinkedIn uses JavaScript-heavy pages
   - **Solution**: Playwright handles dynamic content, but may be slower

3. **Authentication**: Some content requires LinkedIn login
   - **Solution**: Scraper works with public pages; private content not accessible

4. **Structure Changes**: LinkedIn UI changes may break selectors
   - **Solution**: Regular maintenance and selector updates required

5. **Anti-Bot Measures**: LinkedIn may detect automated access
   - **Solution**: Headless mode, user-agent rotation, and request delays

### Legal & Ethical Considerations

1. **Terms of Service**: Review LinkedIn's Terms of Service before scraping
2. **Rate Limits**: Respect LinkedIn's rate limits and usage policies
3. **Data Privacy**: Ensure compliance with data protection regulations (GDPR, etc.)
4. **Public Data Only**: Only scrape publicly available information
5. **Attribution**: Properly attribute data sources

### Best Practices

- Use reasonable delays between requests
- Cache responses to minimize requests
- Monitor for rate limiting and errors
- Implement retry logic with exponential backoff
- Log all scraping activities
- Respect robots.txt and rate limits

### Known Issues

- **Timeout Errors**: Some pages may take longer to load
  - Increase `SCRAPER_PAGE_LOAD_TIMEOUT` if needed
- **Missing Data**: Some pages may have incomplete data
  - Check error logs for details
- **Browser Crashes**: Rare, but may occur with complex pages
  - Automatic retry logic handles most cases

## Bonus Features

### 1. Redis Caching
- **5-minute TTL** for page responses
- **Automatic invalidation** on updates
- **Pattern-based invalidation** for related cache keys
- **Graceful degradation** if Redis unavailable

### 2. AI-Powered Summaries
- **OpenAI integration** for intelligent page analysis
- **Page type classification** (Enterprise, Startup, Agency, etc.)
- **Audience analysis** (size, characteristics)
- **Engagement insights** (level, patterns)
- **Optional feature** - works without OpenAI configured

### 3. Advanced Filtering
- **Multi-criteria filtering** for page searches
- **Partial matching** for industry and name
- **Range filtering** for follower counts
- **Combined filters** for complex queries

### 4. Comprehensive Pagination
- **Reusable pagination utility**
- **Consistent pagination** across all endpoints
- **Metadata included** (total, pages, has_next, has_previous)

### 5. Relationship Management
- **Automatic relationship handling** (pages → posts → comments)
- **Cascade operations** for data integrity
- **Batch operations** for efficiency

### 6. Production Features
- **Docker support** with multi-stage builds
- **Health checks** for all services
- **Structured logging** with configurable levels
- **Environment-based configuration**
- **Database migrations** with Alembic

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=linkedin_insights --cov-report=html

# Run specific test file
pytest tests/test_api/test_pages.py

# Run specific test
pytest tests/test_api/test_pages.py::TestGetPage::test_get_page_from_db

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=linkedin_insights --cov-report=term-missing
```

### Test Coverage

The test suite covers:

- **API Endpoints**: All page, insight, and scraper endpoints
- **Services**: Business logic with mocked dependencies
- **Repositories**: Data access layer
- **Utilities**: Pagination, caching utilities
- **Scraper**: Mocked Playwright tests

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_api/                # API endpoint tests
│   ├── test_pages.py
│   ├── test_insights.py
│   └── test_scraper.py
├── test_services/           # Service layer tests
│   ├── test_insight_service.py
│   └── test_scraper_service.py
├── test_utils/              # Utility tests
│   └── test_pagination.py
└── test_scraper/            # Scraper unit tests
    └── test_linkedin_scraper.py
```

### Test Fixtures

- `db_session`: Test database session (SQLite)
- `client`: FastAPI TestClient with dependency overrides
- `sample_page`: Sample LinkedIn page data
- `sample_posts`: Sample post data

### Mocking

- Playwright browser is mocked in tests
- No actual HTTP requests made
- Database uses in-memory SQLite

## Docker Deployment

See [DOCKER.md](DOCKER.md) for comprehensive Docker documentation.

### Quick Start

```bash
# Build and start all services
docker-compose up -d

# Run migrations
docker-compose exec app alembic upgrade head

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Services

- **app**: FastAPI application (port 8000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)

## Project Structure

```
Linkedin-Insights-Microservice/
├── linkedin_insights/          # Main application package
│   ├── api/                    # API layer
│   │   └── v1/
│   │       └── endpoints/      # API endpoints
│   ├── services/               # Business logic
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── db/                     # Database layer
│   ├── scraper/                # Web scraping
│   └── utils/                  # Utilities
├── tests/                      # Test suite
├── alembic/                    # Database migrations
├── Dockerfile                  # Production Dockerfile
├── docker-compose.yml          # Docker Compose config
└── requirements.txt            # Python dependencies
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Ensure all tests pass
- Follow clean architecture principles

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the excellent web framework
- Playwright for browser automation
- SQLAlchemy for the ORM
- Redis for caching
- OpenAI for AI capabilities

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI, PostgreSQL, Redis, and Playwright**
