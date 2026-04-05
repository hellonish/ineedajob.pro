"""
News Models - Pydantic schemas for news articles.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class NewsArticle(BaseModel):
    """Single news article."""
    title: str = Field(default="", description="Article title")
    description: str = Field(default="", description="Article description/summary")
    url: str = Field(default="", description="Article URL")
    source: str = Field(default="", description="News source name")
    published_at: str = Field(default="", description="Publication date")
    image_url: Optional[str] = Field(default=None, description="Article image URL")


class CompanyNews(BaseModel):
    """News results for a company."""
    company_name: str = Field(default="", description="Company searched")
    articles: List[NewsArticle] = Field(default_factory=list, description="List of articles")
    total_results: int = Field(default=0, description="Total articles found")
    fetched_at: str = Field(default="", description="When the news was fetched")
