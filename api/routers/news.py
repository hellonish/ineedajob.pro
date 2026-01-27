"""
News Router
"""

import sys
import os
from fastapi import APIRouter, Query

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ..schemas import NewsResponse

router = APIRouter(prefix="/api/news", tags=["News"])


@router.get("/{company_name}", response_model=NewsResponse)
async def get_news(
    company_name: str,
    num_articles: int = Query(default=5, le=20)
):
    """Fetch news for a company."""
    from engine.news import fetch_company_news
    
    result = fetch_company_news(company_name, num_articles)
    
    return NewsResponse(
        company_name=result.company_name,
        articles=[
            {
                "title": a.title,
                "description": a.description,
                "url": a.url,
                "source": a.source,
                "published_at": a.published_at
            }
            for a in result.articles
        ],
        total_results=result.total_results
    )
