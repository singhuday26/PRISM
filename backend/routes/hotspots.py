import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from pymongo.errors import PyMongoError
from ..services.analytics import compute_hotspots

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
def hotspots(
    limit: int = Query(5, ge=1, le=50),
    disease: Optional[str] = Query(None, description="Filter by disease")
):
    """Get top hotspots by confirmed cases, optionally filtered by disease."""
    try:
        disease_info = f" for disease: {disease}" if disease else ""
        logger.info(f"Computing top {limit} hotspots{disease_info}")
        data = compute_hotspots(limit=limit, disease=disease)
        logger.info(f"Computed {len(data)} hotspots")
        response = {"hotspots": data, "count": len(data)}
        if disease:
            response["disease"] = disease
        return response
    except PyMongoError as e:
        logger.error(f"Database error computing hotspots: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred while computing hotspots",
        )
    except Exception as e:
        logger.error(f"Unexpected error computing hotspots: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
