"""
Insight model
SQLAlchemy model for LinkedIn insights data
"""
from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from linkedin_insights.models.base import BaseModel


class Insight(BaseModel):
    """LinkedIn insight model"""
    __tablename__ = "insights"
    
    profile_url = Column(String(500), nullable=False, index=True)
    profile_name = Column(String(255), nullable=True)
    title = Column(String(500), nullable=True)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    experience = Column(JSON, nullable=True)
    education = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    # Relationships
    scraper_runs = relationship("ScraperRun", back_populates="insight")


class ScraperRun(BaseModel):
    """Scraper execution run model"""
    __tablename__ = "scraper_runs"
    
    insight_id = Column(Integer, ForeignKey("insights.id"), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    execution_time = Column(String(50), nullable=True)
    
    # Relationships
    insight = relationship("Insight", back_populates="scraper_runs")

