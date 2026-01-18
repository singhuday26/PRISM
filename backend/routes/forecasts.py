import logging
from typing import Optional, Literal
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException, status
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

from backend.db import get_db
from backend.services.forecasting import generate_forecasts

logger = logging.getLogger(__name__)
router = APIRouter()

GranularityType = Literal["yearly", "monthly", "weekly"]


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
    horizon: int = Query(7, ge=1, le=30),
    disease: Optional[str] = Query(None, description="Filter by disease"),
    granularity: GranularityType = Query(
        "monthly", 
        description="Data granularity to use: 'yearly', 'monthly', or 'weekly'. Default is 'monthly' for best forecasting accuracy."
    )
):
    """
    Generate forecasts for all regions, optionally filtered by disease.
    
    The granularity parameter determines which historical data to use:
    - 'yearly': Original yearly data (3 years lookback)
    - 'monthly': Synthetic monthly data (6 months lookback) - RECOMMENDED
    - 'weekly': Synthetic weekly data (12 weeks lookback)
    
    Monthly granularity provides the best balance between signal and noise for forecasting.
    """
    try:
        validated_date = validate_iso_date(date)
        disease_info = f" for disease: {disease}" if disease else ""
        logger.info(
            f"Generating forecasts for date: {validated_date or 'latest'} "
            f"with horizon {horizon}{disease_info} using {granularity} data"
        )
        
        used_date, forecasts = generate_forecasts(validated_date, horizon, disease, granularity)
        logger.info(f"Generated {len(forecasts)} forecasts for date {used_date}")
        
        response = {
            "date": used_date, 
            "forecasts": forecasts, 
            "count": len(forecasts), 
            "horizon": horizon,
            "granularity": granularity
        }
        if disease:
            response["disease"] = disease
        return response
    except HTTPException:
        raise
    except PyMongoError as e:
        logger.error(f"Database error generating forecasts: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred while generating forecasts",
        )
    except Exception as e:
        logger.error(f"Unexpected error generating forecasts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating forecasts",
        )


@router.get("/latest")
def latest(
    region_id: Optional[str] = Query(None),
    horizon: int = Query(7, ge=1, le=30),
    disease: Optional[str] = Query(None, description="Filter by disease")
):
    """Get latest forecasts, optionally filtered by region and/or disease."""
    try:
        db = get_db()
        col = db["forecasts_daily"]

        filter_query = {}
        if disease:
            filter_query["disease"] = disease
        
        latest_doc = col.find_one(filter_query, sort=[("generated_at", DESCENDING)])
        if not latest_doc:
            logger.warning(f"No forecasts found in database{' for disease: ' + disease if disease else ''}")
            return {"date": None, "forecasts": [], "count": 0}

        latest_gen = latest_doc["generated_at"]
        query = {"generated_at": latest_gen}
        if region_id:
            query["region_id"] = region_id
        if disease:
            query["disease"] = disease
            
        logger_msg = f"Fetching latest forecasts with horizon {horizon}"
        if region_id:
            logger_msg = f"Fetching latest forecasts for region: {region_id}"
        if disease:
            logger_msg += f" for disease: {disease}"
        logger.info(logger_msg)

        docs = list(
            col.find(query, {"_id": 0})
            .sort("date", ASCENDING)
            .limit(horizon)
        )
        resolved_date = docs[0]["date"] if docs else None
        
        return {"date": resolved_date, "forecasts": docs, "count": len(docs), "horizon": horizon}
    except PyMongoError as e:
        logger.error(f"Database error fetching latest forecasts: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred while fetching forecasts",
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching latest forecasts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
