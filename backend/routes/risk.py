import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException, status
from pymongo import DESCENDING
from pymongo.errors import PyMongoError

from backend.db import get_db
from backend.services.risk import compute_risk_scores

logger = logging.getLogger(__name__)
router = APIRouter()


def validate_iso_date(date_str: Optional[str]) -> Optional[str]:
    """Validate ISO date format (YYYY-MM-DD)."""
    if date_str is None:
        return None
    try:
        datetime.fromisoformat(date_str)
        return date_str
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD.",
        )


@router.post("/compute")
def compute_risk(
    target_date: Optional[str] = Query(None, description="ISO date YYYY-MM-DD"),
    disease: Optional[str] = Query(None, description="Filter by disease (e.g., 'DENGUE', 'COVID')")
):
    """Compute risk scores for all regions, optionally filtered by disease."""
    try:
        validated_date = validate_iso_date(target_date)
        disease_info = f" for disease: {disease}" if disease else ""
        logger.info(f"Computing risk scores for date: {validated_date or 'latest'}{disease_info}")
        
        used_date, results = compute_risk_scores(validated_date, disease)
        logger.info(f"Computed {len(results)} risk scores for date {used_date}")
        
        response = {"date": used_date, "risk_scores": results, "count": len(results)}
        if disease:
            response["disease"] = disease
        return response
    except HTTPException:
        raise
    except PyMongoError as e:
        logger.error(f"Database error computing risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred while computing risk scores",
        )
    except Exception as e:
        logger.error(f"Unexpected error computing risk: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while computing risk scores",
        )


@router.get("/latest")
def latest_risk(
    region_id: Optional[str] = Query(None, description="Filter by region_id"),
    disease: Optional[str] = Query(None, description="Filter by disease")
):
    """Get latest risk scores, optionally filtered by region and/or disease."""
    try:
        db = get_db()
        risk_col = db["risk_scores"]

        filter_query = {}
        if disease:
            filter_query["disease"] = disease
        
        latest = risk_col.find_one(filter_query, sort=[("date", DESCENDING)])
        if not latest:
            logger.warning(f"No risk scores found in database{' for disease: ' + disease if disease else ''}")
            return {"date": None, "risk_scores": [], "count": 0}

        latest_date = latest["date"]
        query = {"date": latest_date}
        if region_id:
            query["region_id"] = region_id
        if disease:
            query["disease"] = disease
            
        logger_msg = f"Fetching latest risk scores"
        if region_id:
            logger_msg += f" for region: {region_id}"
        if disease:
            logger_msg += f" for disease: {disease}"
        logger.info(logger_msg)

        docs = list(risk_col.find(query, {"_id": 0}).sort("risk_score", DESCENDING))
        
        response = {"date": latest_date, "risk_scores": docs, "count": len(docs)}
        if disease:
            response["disease"] = disease
        return response
    except PyMongoError as e:
        logger.error(f"Database error fetching latest risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred while fetching risk scores",
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching latest risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
