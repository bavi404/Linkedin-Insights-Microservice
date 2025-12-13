"""
Tests for insight service
"""
import pytest
from linkedin_insights.services.insight_service import InsightService
from linkedin_insights.schemas.insight import InsightCreate


def test_create_insight(db_session):
    """Test creating insight via service"""
    service = InsightService(db_session)
    insight_data = InsightCreate(
        profile_url="https://linkedin.com/in/test"
    )
    insight = service.create_insight(insight_data)
    assert insight.id is not None
    assert insight.profile_url == "https://linkedin.com/in/test"

