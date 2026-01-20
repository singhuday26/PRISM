import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException, status
from pymongo import DESCENDING
from pymongo.errors import PyMongoError

from backend.db import get_db
from backend.services.alerts import generate_alerts
from backend.utils.validators import validate_iso_date, validate_disease
from backend.exceptions import DateValidationError, DiseaseValidationError
from backend.schemas.responses import AlertsResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def _handle_validation_error(e: Exception) -> None:
    """Convert validation exceptions to HTTP exceptions."""
    if isinstance(e, (DateValidationError, DiseaseValidationError)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.to_dict()
        )


@router.post("/generate", response_model=AlertsResponse)
def generate(
    date: Optional[str] = Query(None, description="ISO date YYYY-MM-DD"),
    disease: Optional[str] = Query(None, description="Filter by disease")
):
    """Generate alerts based on risk scores, optionally filtered by disease."""
    try:
        validated_date = validate_iso_date(date)
        validated_disease = validate_disease(disease)
        
        disease_info = f" for disease: {validated_disease}" if validated_disease else ""
        logger.info(f"Generating alerts for date: {validated_date or 'latest'}{disease_info}")
        
        used_date, alerts = generate_alerts(validated_date, validated_disease)
        
        logger.info(f"Generated {len(alerts)} alerts for date {used_date}")
        response = {"date": used_date, "alerts": alerts, "count": len(alerts)}
        if validated_disease:
            response["disease"] = validated_disease
        return response
    except (DateValidationError, DiseaseValidationError) as e:
        _handle_validation_error(e)
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


@router.get("/latest", response_model=AlertsResponse)
def latest(
    region_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    disease: Optional[str] = Query(None, description="Filter by disease")
):
    """Get latest alerts, optionally filtered by region and/or disease."""
    try:
        validated_disease = validate_disease(disease)
        
        db = get_db()
        alerts_col = db["alerts"]

        filter_query = {}
        if validated_disease:
            filter_query["disease"] = validated_disease
        
        latest_alert = alerts_col.find_one(filter_query, sort=[("date", DESCENDING)])
        if not latest_alert:
            logger.warning(f"No alerts found in database{' for disease: ' + validated_disease if validated_disease else ''}")
            return {"date": None, "alerts": [], "count": 0}

        latest_date = latest_alert["date"]
        query = {"date": latest_date}
        if region_id:
            query["region_id"] = region_id.strip().upper()
        if validated_disease:
            query["disease"] = validated_disease
            
        logger_msg = f"Fetching latest {limit} alerts"
        if region_id:
            logger_msg = f"Fetching latest alerts for region: {region_id}"
        if validated_disease:
            logger_msg += f" for disease: {validated_disease}"
        logger.info(logger_msg)

        docs = list(
            alerts_col.find(query, {"_id": 0}).sort("risk_score", DESCENDING).limit(limit)
        )
        
        return {"date": latest_date, "alerts": docs, "count": len(docs)}
    except (DateValidationError, DiseaseValidationError) as e:
        _handle_validation_error(e)
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
