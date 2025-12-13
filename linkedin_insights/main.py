"""
Main application entry point
FastAPI app initialization and configuration
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from linkedin_insights.api.v1.router import api_router
from linkedin_insights.utils.config import settings
from linkedin_insights.utils.logging import setup_logging
from linkedin_insights.utils.redis_client import get_redis_client, close_redis_client

# Initialize logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Initialize Redis connection
    await get_redis_client()
    yield
    # Shutdown: Close Redis connection
    await close_redis_client()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.APP_VERSION}

