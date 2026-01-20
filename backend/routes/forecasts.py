import logging
from typing import Optional, Literal
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException, status
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

from backend.db import get_db
from backend.services.forecasting import generate_forecasts
from backend.utils.validators import (
    validate_iso_date, 
    validate_disease, 
    validate_granularity,
    GranularityType,
)
from backend.exceptions import (
    DateValidationError, 
    DiseaseValidationError, 
    GranularityValidationError,
)
from backend.schemas.responses import ForecastsResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def _handle_validation_error(e: Exception) -> None:
    """Convert validation exceptions to HTTP exceptions."""
    if isinstance(e, (DateValidationError, DiseaseValidationError, GranularityValidationError)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.to_dict()
        )


@router.post("/generate", response_model=ForecastsResponse)
def generate(
    date: Optional[str] = Query(None, description="ISO date YYYY-MM-DD"),
    horizon: int = Query(7, ge=1, le=30),
    disease: Optional[str] = Query(None, description="Filter by disease"),
    granularity: Optional[str] = Query(
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
        validated_disease = validate_disease(disease)
        validated_granularity = validate_granularity(granularity)
        
        disease_info = f" for disease: {validated_disease}" if validated_disease else ""
        logger.info(
            f"Generating forecasts for date: {validated_date or 'latest'} "
            f"with horizon {horizon}{disease_info} using {validated_granularity} data"
        )
        
        used_date, forecasts = generate_forecasts(
            validated_date, horizon, validated_disease, validated_granularity
        )
        logger.info(f"Generated {len(forecasts)} forecasts for date {used_date}")
        
        response = {
            "date": used_date, 
            "forecasts": forecasts, 
            "count": len(forecasts), 
            "granularity": validated_granularity
        }
        if validated_disease:
            response["disease"] = validated_disease
        return response
    except (DateValidationError, DiseaseValidationError, GranularityValidationError) as e:
        _handle_validation_error(e)
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


@router.get("/latest", response_model=ForecastsResponse)
def latest(
    region_id: Optional[str] = Query(None),
    horizon: int = Query(7, ge=1, le=30),
    disease: Optional[str] = Query(None, description="Filter by disease")
):
    """Get latest forecasts, optionally filtered by region and/or disease."""
    try:
        validated_disease = validate_disease(disease)
        
        db = get_db()
        col = db["forecasts_daily"]

        filter_query = {}
        if validated_disease:
            filter_query["disease"] = validated_disease
        
        latest_doc = col.find_one(filter_query, sort=[("generated_at", DESCENDING)])
        if not latest_doc:
            logger.warning(f"No forecasts found in database{' for disease: ' + validated_disease if validated_disease else ''}")
            return {"date": None, "forecasts": [], "count": 0}

        latest_gen = latest_doc["generated_at"]
        query = {"generated_at": latest_gen}
        if region_id:
            query["region_id"] = region_id.strip().upper()
        if validated_disease:
            query["disease"] = validated_disease
            
        logger_msg = f"Fetching latest forecasts with horizon {horizon}"
        if region_id:
            logger_msg = f"Fetching latest forecasts for region: {region_id}"
        if validated_disease:
            logger_msg += f" for disease: {validated_disease}"
        logger.info(logger_msg)

        docs = list(
            col.find(query, {"_id": 0})
            .sort("date", ASCENDING)
            .limit(horizon)
        )
        resolved_date = docs[0]["date"] if docs else None
        
        return {"date": resolved_date, "forecasts": docs, "count": len(docs)}
    except (DateValidationError, DiseaseValidationError) as e:
        _handle_validation_error(e)
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


@router.post("/generate-arima", response_model=ForecastsResponse)
def generate_arima(
    date: Optional[str] = Query(None, description="ISO date YYYY-MM-DD"),
    horizon: int = Query(7, ge=1, le=30),
    disease: Optional[str] = Query(None, description="Filter by disease"),
    granularity: Optional[str] = Query(
        "monthly", 
        description="Data granularity: 'yearly', 'monthly', or 'weekly'"
    ),
    use_seasonal: bool = Query(
        True, 
        description="Use seasonal ARIMA (SARIMA) for better seasonality modeling"
    )
):
    """
    Generate ARIMA/SARIMA forecasts for all regions.
    
    This endpoint uses statistical ARIMA models instead of the naive baseline.
    ARIMA provides:
    - Automatic model selection (auto_arima)
    - Confidence intervals based on model uncertainty
    - Seasonal pattern recognition (when use_seasonal=true)
    
    Note: Requires more historical data and takes longer to compute.
    """
    try:
        from backend.services.arima_forecasting import generate_arima_forecasts
        
        validated_date = validate_iso_date(date)
        validated_disease = validate_disease(disease)
        validated_granularity = validate_granularity(granularity)
        
        disease_info = f" for disease: {validated_disease}" if validated_disease else ""
        logger.info(
            f"Generating ARIMA forecasts for date: {validated_date or 'latest'} "
            f"with horizon {horizon}{disease_info} using {validated_granularity} data"
        )
        
        used_date, forecasts = generate_arima_forecasts(
            target_date=validated_date, 
            horizon=horizon, 
            disease=validated_disease, 
            granularity=validated_granularity,
            use_seasonal=use_seasonal,
        )
        logger.info(f"Generated {len(forecasts)} ARIMA forecasts for date {used_date}")
        
        response = {
            "date": used_date, 
            "forecasts": forecasts, 
            "count": len(forecasts), 
            "granularity": validated_granularity
        }
        if validated_disease:
            response["disease"] = validated_disease
        return response
    except (DateValidationError, DiseaseValidationError, GranularityValidationError) as e:
        _handle_validation_error(e)
    except ImportError as e:
        logger.error(f"ARIMA dependencies not installed: {e}")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="ARIMA forecasting requires pmdarima. Run: pip install pmdarima statsmodels",
        )
    except HTTPException:
        raise
    except PyMongoError as e:
        logger.error(f"Database error generating ARIMA forecasts: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred while generating ARIMA forecasts",
        )
    except Exception as e:
        logger.error(f"Unexpected error generating ARIMA forecasts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating ARIMA forecasts",
        )
