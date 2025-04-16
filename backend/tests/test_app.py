# tests/test_app.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import app, get_db, Base, ScrapedPage

# Create an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)

# Override the get_db dependency to use our test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create a test client
client = TestClient(app)

def test_scrape_url():
    """Test the scrape endpoint with a valid URL"""
    # Using a static website for reliable testing
    response = client.post(
        "/scrape/",
        json={"url": "https://example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["url"] == "https://example.com"
    assert "title" in data
    assert "content" in data
    assert "scraped_at" in data
    assert "last_accessed" in data

def test_get_pages_empty():
    """Test getting pages when database is empty"""
    # Clear the database first
    db = TestingSessionLocal()
    db.query(ScrapedPage).delete()
    db.commit()
    
    response = client.get("/pages/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_pages_with_data():
    """Test getting pages when database has data"""
    # Add test data
    db = TestingSessionLocal()
    test_page = ScrapedPage(
        url="https://test-url.com",
        title="Test Title",
        content="Test Content"
    )
    db.add(test_page)
    db.commit()
    
    response = client.get("/pages/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(page["url"] == "https://test-url.com" for page in data)

def test_get_page_by_id():
    """Test getting a specific page by ID"""
    # Add test data and get its ID
    db = TestingSessionLocal()
    test_page = ScrapedPage(
        url="https://get-by-id-test.com",
        title="Get By ID Test",
        content="Test Content for Get By ID"
    )
    db.add(test_page)
    db.commit()
    db.refresh(test_page)
    page_id = test_page.id
    
    response = client.get(f"/pages/{page_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == page_id
    assert data["url"] == "https://get-by-id-test.com"
    assert data["title"] == "Get By ID Test"

def test_get_nonexistent_page():
    """Test getting a page that doesn't exist"""
    # Using a large ID that's unlikely to exist
    response = client.get("/pages/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Page not found"}

def test_search_pages():
    """Test searching pages by content or title"""
    # Add test data
    db = TestingSessionLocal()
    test_page = ScrapedPage(
        url="https://search-test.com",
        title="Search Test Title",
        content="This is unique searchable content"
    )
    db.add(test_page)
    db.commit()
    
    # Search for a term that should match
    response = client.get("/search/?query=unique+searchable")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(page["url"] == "https://search-test.com" for page in data)
    
    # Search for a term that shouldn't match
    response = client.get("/search/?query=this+should+not+match+anything")
    assert response.status_code == 200
    assert response.json() == []
