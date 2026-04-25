import logging
from typing import Optional, Literal
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException, status
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

from backend.db import get_db
from backend.services.forecasting import generate_forecasts
from backend.services.derived_data_bootstrap import ensure_derived_data_for_disease
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
from backend.routes.helpers import handle_validation_error

logger = logging.getLogger(__name__)
router = APIRouter()


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

        effective_granularity = validated_granularity
        if forecasts:
            effective_granularity = forecasts[0].get(
                "source_granularity",
                validated_granularity,
            )
        
        response = {
            "date": used_date, 
            "forecasts": forecasts, 
            "count": len(forecasts), 
            "granularity": effective_granularity
        }
        if validated_disease:
            response["disease"] = validated_disease
        return response
    except (DateValidationError, DiseaseValidationError, GranularityValidationError) as e:
        handle_validation_error(e)
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

        # Build query — scope to disease and optional region
        query: dict = {}
        if validated_disease:
            query["disease"] = validated_disease
        if region_id:
            query["region_id"] = region_id.strip().upper()

        # Get the most recent `horizon` forecasts by descending date,
        # then reverse so they're returned chronologically ascending.
        # This avoids the brittle generated_at batch-matching approach.
        docs = list(
            col.find(query, {"_id": 0})
            .sort("date", DESCENDING)
            .limit(horizon)
        )

        if not docs:
            if validated_disease:
                ensure_derived_data_for_disease(
                    validated_disease,
                    forecast_horizon=horizon,
                    forecast_granularity="monthly",
                )
                docs = list(
                    col.find(query, {"_id": 0})
                    .sort("date", DESCENDING)
                    .limit(horizon)
                )

        if not docs:
            logger.warning(
                f"No forecasts found"
                f"{' for region: ' + region_id if region_id else ''}"
                f"{' disease: ' + validated_disease if validated_disease else ''}"
            )
            response = {"date": None, "forecasts": [], "count": 0}
            if validated_disease:
                response["disease"] = validated_disease
            return response

        # Reverse to get chronological order
        docs = list(reversed(docs))
        resolved_date = docs[0]["date"]

        logger.info(
            f"Returning {len(docs)} forecasts"
            f"{' for region: ' + region_id if region_id else ''}"
            f"{' disease: ' + validated_disease if validated_disease else ''}"
        )
        return {"date": resolved_date, "forecasts": docs, "count": len(docs)}

    except (DateValidationError, DiseaseValidationError) as e:
        handle_validation_error(e)
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
        handle_validation_error(e)
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
