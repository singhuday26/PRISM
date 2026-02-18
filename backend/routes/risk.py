import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException, status
from pymongo import DESCENDING
from pymongo.errors import PyMongoError

from backend.db import get_db
from backend.services.risk import compute_risk_scores
from backend.utils.validators import validate_iso_date, validate_disease
from backend.exceptions import DateValidationError, DiseaseValidationError
from backend.schemas.responses import RiskScoreResponse as RiskScoreListResponse
from backend.routes.helpers import handle_validation_error

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/compute", response_model=RiskScoreListResponse)
def compute_risk(
    target_date: Optional[str] = Query(None, description="ISO date YYYY-MM-DD"),
    disease: Optional[str] = Query(None, description="Filter by disease (e.g., 'DENGUE', 'COVID')")
):
    """Compute risk scores for all regions, optionally filtered by disease."""
    try:
        validated_date = validate_iso_date(target_date)
        validated_disease = validate_disease(disease)
        
        disease_info = f" for disease: {validated_disease}" if validated_disease else ""
        logger.info(f"Computing risk scores for date: {validated_date or 'latest'}{disease_info}")
        
        used_date, results = compute_risk_scores(validated_date, validated_disease)
        logger.info(f"Computed {len(results)} risk scores for date {used_date}")
        
        response = {"date": used_date, "risk_scores": results, "count": len(results)}
        if validated_disease:
            response["disease"] = validated_disease
        return response
    except (DateValidationError, DiseaseValidationError) as e:
        handle_validation_error(e)
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


@router.get("/latest", response_model=RiskScoreListResponse)
def latest_risk(
    region_id: Optional[str] = Query(None, description="Filter by region_id"),
    disease: Optional[str] = Query(None, description="Filter by disease")
):
    """Get latest risk scores, optionally filtered by region and/or disease."""
    try:
        validated_disease = validate_disease(disease)
        
        db = get_db()
        risk_col = db["risk_scores"]

        filter_query = {}
        if validated_disease:
            filter_query["disease"] = validated_disease
        
        latest = risk_col.find_one(filter_query, sort=[("date", DESCENDING)])
        if not latest:
            logger.warning(f"No risk scores found in database{' for disease: ' + validated_disease if validated_disease else ''}")
            return {"date": None, "risk_scores": [], "count": 0}

        latest_date = latest["date"]
        query = {"date": latest_date}
        if region_id:
            query["region_id"] = region_id.strip().upper()
        if validated_disease:
            query["disease"] = validated_disease
            
        logger_msg = f"Fetching latest risk scores"
        if region_id:
            logger_msg += f" for region: {region_id}"
        if validated_disease:
            logger_msg += f" for disease: {validated_disease}"
        logger.info(logger_msg)

        docs = list(risk_col.find(query, {"_id": 0}).sort("risk_score", DESCENDING))
        
        response = {"date": latest_date, "risk_scores": docs, "count": len(docs)}
        if validated_disease:
            response["disease"] = validated_disease
        return response
    except (DateValidationError, DiseaseValidationError) as e:
        handle_validation_error(e)
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
