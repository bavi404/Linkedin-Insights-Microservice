"""
Pytest configuration and fixtures
Shared test fixtures and configuration
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from linkedin_insights.main import app
from linkedin_insights.db.base import Base, get_db
from linkedin_insights.models.insight import Insight, ScraperRun
from linkedin_insights.models.linkedin import LinkedInPage, Post, Comment, SocialMediaUser

# Test database URL (use SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Don't close, handled by fixture
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_page(db_session):
    """Create a sample LinkedIn page for testing"""
    page = LinkedInPage(
        page_id="test-company",
        name="Test Company",
        url="https://www.linkedin.com/company/test-company",
        linkedin_internal_id="123456",
        description="A test company",
        industry="Technology",
        total_followers=1000,
        head_count=50,
        specialities="Software, AI",
        profile_image_url="https://example.com/image.jpg"
    )
    db_session.add(page)
    db_session.commit()
    db_session.refresh(page)
    return page


@pytest.fixture
def sample_pages(db_session):
    """Create multiple sample pages for testing"""
    pages = [
        LinkedInPage(
            page_id=f"company-{i}",
            name=f"Company {i}",
            url=f"https://www.linkedin.com/company/company-{i}",
            industry="Technology" if i % 2 == 0 else "Finance",
            total_followers=1000 * i,
            head_count=10 * i
        )
        for i in range(1, 11)
    ]
    for page in pages:
        db_session.add(page)
    db_session.commit()
    for page in pages:
        db_session.refresh(page)
    return pages


@pytest.fixture
def sample_posts(db_session, sample_page):
    """Create sample posts for testing"""
    posts = [
        Post(
            post_id=f"post-{i}",
            page_id=sample_page.id,
            content=f"Post content {i}",
            like_count=10 * i,
            comment_count=5 * i,
            posted_at=datetime.utcnow()
        )
        for i in range(1, 6)
    ]
    for post in posts:
        db_session.add(post)
    db_session.commit()
    for post in posts:
        db_session.refresh(post)
    return posts

