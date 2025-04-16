# app.py - FastAPI Backend
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, HttpUrl
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from typing import List, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/webscraper")

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define SQLAlchemy models
class ScrapedPage(Base):
    __tablename__ = "scraped_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=func.now())
    last_accessed = Column(DateTime, default=func.now(), onupdate=func.now())

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for API
class PageBase(BaseModel):
    url: HttpUrl
    
class PageCreate(PageBase):
    pass

class PageResponse(PageBase):
    id: int
    title: Optional[str] = None
    content: Optional[str] = None
    scraped_at: datetime
    last_accessed: datetime
    
    class Config:
        orm_mode = True

# FastAPI app initialization
app = FastAPI(title="Web Scraper API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Web scraping function
def scrape_webpage(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Get the page title
        title = soup.title.string if soup.title else "No title found"
        
        # Get the main content (this is a simplistic approach, customize for specific websites)
        content = soup.get_text(separator="\n", strip=True)
        
        return {
            "title": title,
            "content": content[:100000]  # Limit content size
        }
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {"title": "Error scraping page", "content": f"Failed to scrape: {str(e)}"}

# Background task for scraping
def background_scrape(url: str, db: Session):
    try:
        scraped_data = scrape_webpage(url)
        
        # Update database
        db_page = db.query(ScrapedPage).filter(ScrapedPage.url == url).first()
        
        if db_page:
            db_page.title = scraped_data["title"]
            db_page.content = scraped_data["content"]
            db_page.last_accessed = datetime.now()
        else:
            db_page = ScrapedPage(
                url=url,
                title=scraped_data["title"],
                content=scraped_data["content"]
            )
            db.add(db_page)
            
        db.commit()
        logger.info(f"Successfully scraped and saved...: {url}")
        
    except Exception as e:
        logger.error(f"Background scraping error for {url}: {str(e)}")
        db.rollback()

# API endpoints
@app.post("/scrape/", response_model=PageResponse)
def scrape_url(page: PageCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    url = str(page.url)
    
    # Check if the page is already in the database
    db_page = db.query(ScrapedPage).filter(ScrapedPage.url == url).first()
    
    if db_page:
        # Update last_accessed timestamp
        db_page.last_accessed = datetime.now()
        db.commit()
        
        # If content already exists, return it immediately
        if db_page.content:
            # But still update in the background to refresh
            background_tasks.add_task(background_scrape, url, SessionLocal())
            return db_page
    
    # If page doesn't exist or has no content, scrape immediately
    scraped_data = scrape_webpage(url)
    
    if not db_page:
        # Create new record
        db_page = ScrapedPage(
            url=url,
            title=scraped_data["title"],
            content=scraped_data["content"]
        )
        db.add(db_page)
    else:
        # Update existing record
        db_page.title = scraped_data["title"]
        db_page.content = scraped_data["content"]
    
    db.commit()
    db.refresh(db_page)
    
    return db_page

@app.get("/pages/", response_model=List[PageResponse])
def get_pages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ScrapedPage).offset(skip).limit(limit).all()

@app.get("/pages/{page_id}", response_model=PageResponse)
def get_page(page_id: int, db: Session = Depends(get_db)):
    db_page = db.query(ScrapedPage).filter(ScrapedPage.id == page_id).first()
    if db_page is None:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Update last_accessed timestamp
    db_page.last_accessed = datetime.now()
    db.commit()
    
    return db_page

@app.get("/search/", response_model=List[PageResponse])
def search_pages(query: str, db: Session = Depends(get_db)):
    if not query:
        return []
    
    # Simple search implementation - can be improved with full-text search
    results = db.query(ScrapedPage).filter(
        ScrapedPage.content.ilike(f"%{query}%") | 
        ScrapedPage.title.ilike(f"%{query}%")
    ).all()
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
