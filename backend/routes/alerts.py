import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException, status
from pymongo import DESCENDING
from pymongo.errors import PyMongoError

from backend.db import get_db
from backend.services.alerts import generate_alerts

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


@router.post("/generate")
def generate(
    date: Optional[str] = Query(None, description="ISO date YYYY-MM-DD"),
    disease: Optional[str] = Query(None, description="Filter by disease")
):
    """Generate alerts based on risk scores, optionally filtered by disease."""
    try:
        validated_date = validate_iso_date(date)
        disease_info = f" for disease: {disease}" if disease else ""
        logger.info(f"Generating alerts for date: {validated_date or 'latest'}{disease_info}")
        
        used_date, alerts = generate_alerts(validated_date, disease)
        
        logger.info(f"Generated {len(alerts)} alerts for date {used_date}")
        response = {"date": used_date, "alerts": alerts, "count": len(alerts)}
        if disease:
            response["disease"] = disease
        return response
    except HTTPException:
        raise
    except PyMongoError as e:
        logger.error(f"Database error generating alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred while generating alerts",
        )
    except Exception as e:
        logger.error(f"Unexpected error generating alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating alerts",
        )


@router.get("/latest")
def latest(
    region_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    disease: Optional[str] = Query(None, description="Filter by disease")
):
    """Get latest alerts, optionally filtered by region and/or disease."""
    try:
        db = get_db()
        alerts_col = db["alerts"]

        filter_query = {}
        if disease:
            filter_query["disease"] = disease
        
        latest_alert = alerts_col.find_one(filter_query, sort=[("date", DESCENDING)])
        if not latest_alert:
            logger.warning(f"No alerts found in database{' for disease: ' + disease if disease else ''}")
            return {"date": None, "alerts": [], "count": 0}

        latest_date = latest_alert["date"]
        query = {"date": latest_date}
        if region_id:
            query["region_id"] = region_id
        if disease:
            query["disease"] = disease
            
        logger_msg = f"Fetching latest {limit} alerts"
        if region_id:
            logger_msg = f"Fetching latest alerts for region: {region_id}"
        if disease:
            logger_msg += f" for disease: {disease}"
        logger.info(logger_msg)

        docs = list(
            alerts_col.find(query, {"_id": 0}).sort("risk_score", DESCENDING).limit(limit)
        )
        
        return {"date": latest_date, "alerts": docs, "count": len(docs)}
    except PyMongoError as e:
        logger.error(f"Database error fetching latest alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred while fetching alerts",
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching latest alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
