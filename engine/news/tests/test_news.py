"""Test News Fetcher"""
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from engine.news import fetch_company_news


def test_news_fetcher():
    print(f"\n{'='*70}")
    print("Testing News Fetcher")
    print(f"{'='*70}\n")
    
    # Test with Lord Abbett (from job posting)
    company_name = "Lord Abbett"
    
    print(f"🔍 Searching news for: {company_name}")
    
    try:
        result = fetch_company_news(company_name, num_articles=5)
    except ValueError as e:
        print(f"⚠ {e}")
        print("\nTo test, set NEWSAPI_KEY in your .env file")
        return None
    
    # Display results
    print(f"\n{'='*70}")
    print(f"NEWS RESULTS FOR: {result.company_name}")
    print(f"{'='*70}\n")
    
    print(f"📊 Total results: {result.total_results}")
    print(f"📅 Fetched at: {result.fetched_at}")
    
    print(f"\n📰 Articles ({len(result.articles)}):")
    for i, article in enumerate(result.articles, 1):
        print(f"\n  {i}. {article.title}")
        print(f"     Source: {article.source}")
        print(f"     Published: {article.published_at}")
        print(f"     URL: {article.url[:60]}...")
        if article.description:
            print(f"     Summary: {article.description[:100]}...")
    
    # Save output
    test_dir = os.path.dirname(__file__)
    output_path = os.path.join(test_dir, 'news_result.json')
    with open(output_path, 'w') as f:
        json.dump(result.model_dump(), f, indent=2)
    
    print(f"\n💾 Saved to: news_result.json")
    print(f"{'='*70}\n")
    
    return result


if __name__ == "__main__":
    test_news_fetcher()
