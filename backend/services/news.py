import logging
from datetime import datetime
from typing import List, Optional
from ..db import get_db

logger = logging.getLogger(__name__)

def fetch_latest_news(disease: Optional[str] = None, limit: int = 10) -> List[dict]:
    """
    Fetch news articles related to a disease.
    In a real-world scenario, this would connect to external APIs like NewsAPI, GDELT, or RSS feeds.
    Currently, it retrieves from the local news_articles collection.
    """
    db = get_db()
    query = {}
    if disease:
        # Support both 'dengue' and 'DENGUE'
        query["extracted_diseases"] = {"$in": [disease.upper(), disease.lower()]}
    
    articles = list(db["news_articles"].find(query).sort("published_at", -1).limit(limit))
    for article in articles:
        article["_id"] = str(article["_id"])
    return articles

def ingest_simulated_news():
    """
    Seed the database with simulated health news signals.
    This demonstrates how the platform handles incoming textual signals.
    """
    db = get_db()
    simulated_articles = [
        {
            "title": "Unusual surge in febrile illness reported in suburban Mumbai",
            "source": "State Health Monitor",
            "published_at": datetime.utcnow(),
            "url": "https://example.org/news/1",
            "content": "Health officials in Mumbai are monitoring a localized surge in patients with high fever and joint pain...",
            "extracted_diseases": ["DENGUE", "CHIKUNGUNYA"],
            "extracted_locations": ["Mumbai", "Maharashtra"],
            "relevance_score": 0.85,
            "ingested_at": datetime.utcnow()
        },
        {
            "title": "Climate warning: Monsoon patterns likely to favor malaria transmission",
            "source": "Environmental Bio-Risk",
            "published_at": datetime.utcnow(),
            "url": "https://example.org/news/2",
            "content": "A new research paper suggests that shifting rainfall patterns in Karnataka provide ideal breeding grounds...",
            "extracted_diseases": ["MALARIA"],
            "extracted_locations": ["Karnataka"],
            "relevance_score": 0.72,
            "ingested_at": datetime.utcnow()
        },
        {
            "title": "Hospitals in Delhi on alert for respiratory illness clusters",
            "source": "National Health Record",
            "published_at": datetime.utcnow(),
            "url": "https://example.org/news/3",
            "content": "Multiple primary health centers in North Delhi have reported an uptick in influenza-like illnesses...",
            "extracted_diseases": ["INFLUENZA", "COVID"],
            "extracted_locations": ["Delhi"],
            "relevance_score": 0.78,
            "ingested_at": datetime.utcnow()
        }
    ]
    
    for article in simulated_articles:
        db["news_articles"].update_one(
            {"title": article["title"]},
            {"$set": article},
            upsert=True
        )
    logger.info(f"Ingested {len(simulated_articles)} simulated news articles.")

def ensure_news_indexes():
    """Ensure indexes for news searching."""
    db = get_db()
    db["news_articles"].create_index([("extracted_diseases", 1)])
    db["news_articles"].create_index([("published_at", -1)])
    db["news_articles"].create_index([("title", 1)], unique=True)
