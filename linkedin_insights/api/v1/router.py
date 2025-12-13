"""
API v1 router
Main router that includes all v1 endpoints
"""
from fastapi import APIRouter

from linkedin_insights.api.v1.endpoints import insights, scraper, pages, ai_summary

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
api_router.include_router(scraper.router, prefix="/scraper", tags=["scraper"])
api_router.include_router(pages.router, prefix="/pages", tags=["pages"])
# AI summary endpoints (optional, requires OpenAI API key)
api_router.include_router(ai_summary.router, tags=["ai-summary"])

