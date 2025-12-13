"""
Insight service
Async business logic for insight operations
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from linkedin_insights.models.insight import Insight
from linkedin_insights.schemas.insight import InsightCreate, InsightUpdate
from linkedin_insights.db.repository import BaseRepository


class InsightRepository(BaseRepository[Insight]):
    """Repository for Insight model"""
    pass


class InsightService:
    """Async service for insight business logic"""
    
    def __init__(self, db: AsyncSession):
        self.repository = InsightRepository(Insight, db)
    
    async def get_insight(self, insight_id: int) -> Optional[Insight]:
        """Get insight by ID"""
        return await self.repository.get(insight_id)
    
    async def get_insights(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Insight]:
        """Get all insights with pagination"""
        return await self.repository.get_all(skip=skip, limit=limit)
    
    async def create_insight(self, insight_data: InsightCreate) -> Insight:
        """Create new insight"""
        return await self.repository.create(insight_data.model_dump())
    
    async def update_insight(
        self, 
        insight_id: int, 
        insight_data: InsightUpdate
    ) -> Optional[Insight]:
        """Update existing insight"""
        insight = await self.repository.get(insight_id)
        if not insight:
            return None
        return await self.repository.update(insight, insight_data.model_dump(exclude_unset=True))
    
    async def delete_insight(self, insight_id: int) -> bool:
        """Delete insight"""
        return await self.repository.delete(insight_id)
