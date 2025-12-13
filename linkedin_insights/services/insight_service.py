"""
Insight service
Business logic for insight operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from linkedin_insights.models.insight import Insight
from linkedin_insights.schemas.insight import InsightCreate, InsightUpdate
from linkedin_insights.db.repository import BaseRepository


class InsightRepository(BaseRepository[Insight]):
    """Repository for Insight model"""
    pass


class InsightService:
    """Service for insight business logic"""
    
    def __init__(self, db: Session):
        self.repository = InsightRepository(Insight, db)
    
    def get_insight(self, insight_id: int) -> Optional[Insight]:
        """Get insight by ID"""
        return self.repository.get(insight_id)
    
    def get_insights(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Insight]:
        """Get all insights with pagination"""
        return self.repository.get_all(skip=skip, limit=limit)
    
    def create_insight(self, insight_data: InsightCreate) -> Insight:
        """Create new insight"""
        return self.repository.create(insight_data.model_dump())
    
    def update_insight(
        self, 
        insight_id: int, 
        insight_data: InsightUpdate
    ) -> Optional[Insight]:
        """Update existing insight"""
        insight = self.repository.get(insight_id)
        if not insight:
            return None
        return self.repository.update(insight, insight_data.model_dump(exclude_unset=True))
    
    def delete_insight(self, insight_id: int) -> bool:
        """Delete insight"""
        return self.repository.delete(insight_id)

