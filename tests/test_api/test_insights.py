"""
Tests for insights endpoints
"""
import pytest
from fastapi import status


def test_create_insight(client):
    """Test creating an insight"""
    response = client.post(
        "/api/v1/insights/",
        json={
            "profile_url": "https://linkedin.com/in/test",
            "profile_name": "Test User"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["profile_name"] == "Test User"


def test_get_insights(client):
    """Test getting all insights"""
    response = client.get("/api/v1/insights/")
    assert response.status_code == status.HTTP_200_OK
    assert "items" in response.json()

