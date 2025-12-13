"""
Insights endpoints
Async CRUD operations for insights
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from linkedin_insights.db.base import get_db
from linkedin_insights.schemas.insight import (
    InsightCreate,
    InsightUpdate,
    InsightResponse,
    InsightListResponse,
)
from linkedin_insights.services.insight_service import InsightService

router = APIRouter()


@router.get("/", response_model=InsightListResponse)
async def get_insights(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all insights with pagination"""
    service = InsightService(db)
    insights = await service.get_insights(skip=skip, limit=limit)
    return {
        "items": insights,
        "total": len(insights),
        "page": skip // limit + 1,
        "page_size": limit,
    }


@router.get("/{insight_id}", response_model=InsightResponse)
async def get_insight(
    insight_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get insight by ID"""
    service = InsightService(db)
    insight = await service.get_insight(insight_id)
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
    return insight


@router.post("/", response_model=InsightResponse, status_code=status.HTTP_201_CREATED)
async def create_insight(
    insight_data: InsightCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new insight"""
    service = InsightService(db)
    return await service.create_insight(insight_data)


@router.put("/{insight_id}", response_model=InsightResponse)
async def update_insight(
    insight_id: int,
    insight_data: InsightUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update existing insight"""
    service = InsightService(db)
    insight = await service.update_insight(insight_id, insight_data)
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
    return insight


@router.delete("/{insight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_insight(
    insight_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete insight"""
    service = InsightService(db)
    if not await service.delete_insight(insight_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
