"""Evaluation routes for model performance metrics."""
import logging
from typing import Optional

from fastapi import APIRouter, Query, HTTPException, status
from pymongo.errors import PyMongoError

from backend.services.evaluation import evaluate_forecast

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/forecast")
def get_forecast_evaluation(
    region_id: str = Query(..., description="Region ID to evaluate"),
    date: Optional[str] = Query(None, description="Starting date (YYYY-MM-DD)"),
    horizon: int = Query(7, ge=1, le=30, description="Forecast horizon in days"),
):
    """
    Evaluate forecast accuracy for a region.
    
    Compares forecast predictions with actual observed values and returns
    MAE (Mean Absolute Error) and MAPE (Mean Absolute Percentage Error).
    """
    try:
        logger.info(f"Evaluating forecast for region {region_id}, horizon {horizon}")
        
        result = evaluate_forecast(region_id, date, horizon)
        
        if result.get("error"):
            logger.warning(f"Evaluation returned error: {result['error']}")
        
        return result
        
    except PyMongoError as e:
        logger.error(f"Database error during evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred during evaluation",
        )
    except Exception as e:
        logger.error(f"Unexpected error during evaluation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during evaluation",
        )
