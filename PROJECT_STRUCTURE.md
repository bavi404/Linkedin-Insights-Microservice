# LinkedIn Insights Microservice - Project Structure

## Folder Structure

```
Linkedin-Insights-Microservice/
│
├── linkedin_insights/              # Main application package
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # FastAPI app entry point
│   │
│   ├── api/                        # API layer (presentation)
│   │   ├── __init__.py
│   │   ├── middleware.py           # Custom middleware (logging, etc.)
│   │   └── v1/                     # API version 1
│   │       ├── __init__.py
│   │       ├── router.py           # Main API router
│   │       ├── dependencies.py     # Shared API dependencies
│   │       └── endpoints/          # API endpoints
│   │           ├── __init__.py
│   │           ├── insights.py     # Insights CRUD endpoints
│   │           └── scraper.py      # Scraper endpoints
│   │
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── insight_service.py      # Insight business logic
│   │   └── scraper_service.py      # Scraper business logic
│   │
│   ├── models/                     # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py                 # Base model with common fields
│   │   └── insight.py              # Insight and ScraperRun models
│   │
│   ├── schemas/                    # Pydantic schemas (validation)
│   │   ├── __init__.py
│   │   ├── base.py                 # Base schemas
│   │   ├── insight.py               # Insight request/response schemas
│   │   └── scraper.py               # Scraper request/response schemas
│   │
│   ├── db/                         # Database layer
│   │   ├── __init__.py
│   │   ├── base.py                 # SQLAlchemy engine, session, base
│   │   └── repository.py           # Repository pattern base class
│   │
│   ├── scraper/                    # Scraper layer
│   │   ├── __init__.py
│   │   └── linkedin_scraper.py     # LinkedIn scraping logic
│   │
│   └── utils/                      # Utilities
│       ├── __init__.py
│       ├── config.py               # Pydantic BaseSettings configuration
│       ├── logging.py              # Logging setup
│       └── helpers.py              # Helper functions
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_api/                   # API endpoint tests
│   │   ├── __init__.py
│   │   ├── test_insights.py
│   │   └── test_scraper.py
│   ├── test_services/              # Service layer tests
│   │   ├── __init__.py
│   │   └── test_insight_service.py
│   └── test_scraper/               # Scraper tests
│       ├── __init__.py
│       └── test_linkedin_scraper.py
│
├── alembic/                        # Database migrations
│   ├── env.py                      # Alembic environment config
│   └── script.py.mako              # Migration template
│
├── logs/                           # Application logs (created at runtime)
│
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration
├── alembic.ini                     # Alembic configuration
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Docker Compose setup
├── README.md                       # Project documentation
└── PROJECT_STRUCTURE.md            # This file
```

## Architecture Layers

### 1. **API Layer** (`api/`)
   - FastAPI routers and endpoints
   - Request/response handling
   - Middleware and dependencies

### 2. **Services Layer** (`services/`)
   - Business logic
   - Orchestrates data flow
   - Coordinates between repositories and scrapers

### 3. **Models Layer** (`models/`)
   - SQLAlchemy ORM models
   - Database table definitions

### 4. **Schemas Layer** (`schemas/`)
   - Pydantic validation schemas
   - Request/response DTOs

### 5. **Database Layer** (`db/`)
   - Database connection management
   - Session handling
   - Repository pattern implementation

### 6. **Scraper Layer** (`scraper/`)
   - LinkedIn profile scraping logic
   - Data extraction and parsing

### 7. **Utils Layer** (`utils/`)
   - Configuration management (Pydantic BaseSettings)
   - Logging setup
   - Helper functions

## Key Features

- ✅ Clean Architecture with separated layers
- ✅ Pydantic BaseSettings for configuration
- ✅ Structured logging setup
- ✅ SQLAlchemy ORM with repository pattern
- ✅ Alembic for database migrations
- ✅ Comprehensive test structure
- ✅ Docker support
- ✅ API versioning (v1)

