from fastapi import APIRouter, Query, Depends, status
from typing import List, Optional
from ..services import news as news_service
from ..schemas.responses import NewsResponse

router = APIRouter(prefix="/news", tags=["news"])

@router.get("/", response_model=NewsResponse)
async def get_news(
    disease: Optional[str] = Query(None, description="Filter news by disease name"),
    limit: int = Query(10, ge=1, le=50, description="Number of articles to return")
):
    """
    Get the latest health news signals and epidemiological articles.
    Provides early warning signals for potential outbreaks.
    """
    articles = news_service.fetch_latest_news(disease=disease, limit=limit)
    return {
        "articles": articles,
        "count": len(articles),
        "disease": disease
    }

@router.post("/ingest-simulated", status_code=status.HTTP_201_CREATED)
async def trigger_simulated_ingestion():
    """
    Manually trigger an ingestion of simulated news articles.
    Useful for demonstration and testing of the early warning feed.
    """
    news_service.ingest_simulated_news()
    return {"message": "Simulated ingestion successful"}
