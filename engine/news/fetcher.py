"""
News Fetcher - Get latest news articles for a company using NewsAPI.
"""

import os
from typing import Optional
from datetime import datetime
import httpx
from dotenv import load_dotenv
from .models import NewsArticle, CompanyNews

# Load .env file
load_dotenv()


class NewsFetcher:
    """
    Fetches latest news for a company using NewsAPI.
    
    Requires NEWSAPI_KEY environment variable.
    Get your free API key at: https://newsapi.org/
    """
    
    BASE_URL = "https://newsapi.org/v2/everything"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NEWSAPI_KEY")
        if not self.api_key:
            raise ValueError(
                "NEWSAPI_KEY not found. Set it in .env file or pass as parameter. "
                "Get your free key at: https://newsapi.org/"
            )
    
    def fetch(
        self,
        company_name: str,
        num_articles: int = 5,
        language: str = "en"
    ) -> CompanyNews:
        """
        Fetch latest news articles for a company.
        
        Args:
            company_name: Company name to search for
            num_articles: Number of articles to return (default 5)
            language: Language code (default "en")
            
        Returns:
            CompanyNews with list of articles
        """
        print(f"📰 Fetching news for: {company_name}")
        
        params = {
            "q": company_name,
            "apiKey": self.api_key,
            "pageSize": num_articles,
            "language": language,
            "sortBy": "publishedAt"  # Latest first
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as e:
            print(f"⚠ Error fetching news: {e}")
            return CompanyNews(
                company_name=company_name,
                articles=[],
                total_results=0,
                fetched_at=datetime.now().isoformat()
            )
        
        articles = []
        for article in data.get("articles", []):
            articles.append(NewsArticle(
                title=article.get("title", ""),
                description=article.get("description", ""),
                url=article.get("url", ""),
                source=article.get("source", {}).get("name", ""),
                published_at=article.get("publishedAt", ""),
                image_url=article.get("urlToImage")
            ))
        
        result = CompanyNews(
            company_name=company_name,
            articles=articles,
            total_results=data.get("totalResults", 0),
            fetched_at=datetime.now().isoformat()
        )
        
        print(f"✅ Found {len(articles)} articles")
        return result


# Convenience function
def fetch_company_news(
    company_name: str,
    num_articles: int = 5,
    api_key: Optional[str] = None
) -> CompanyNews:
    """
    Convenience function to fetch company news.
    
    Args:
        company_name: Company to search for
        num_articles: Number of articles (default 5)
        api_key: Optional NewsAPI key
        
    Returns:
        CompanyNews with articles
    """
    fetcher = NewsFetcher(api_key)
    return fetcher.fetch(company_name, num_articles)
