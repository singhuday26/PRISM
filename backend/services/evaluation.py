"""Evaluation service for forecast accuracy metrics."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Optional

from pymongo import ASCENDING

from backend.db import get_db

logger = logging.getLogger(__name__)


def safe_mape(actual: float, predicted: float) -> Optional[float]:
    """Calculate MAPE safely, handling divide-by-zero."""
    if actual == 0 or abs(actual) < 1e-10:
        return None
    return abs((actual - predicted) / actual) * 100


def evaluate_forecast(
    region_id: str, date: Optional[str] = None, horizon: int = 7
) -> Dict:
    """
    Evaluate forecast accuracy by comparing predictions with actual values.
    
    Args:
        region_id: Region to evaluate
        date: Starting date for forecast (default: latest forecast)
        horizon: Number of days to evaluate
        
    Returns:
        Dictionary with MAE, MAPE, and metadata
    """
    try:
        db = get_db()
        forecasts_col = db["forecasts_daily"]
        cases_col = db["cases_daily"]
        
        # Get forecasts for this region
        query = {"region_id": region_id}
        if date:
            query["date"] = {"$gte": date}
        
        forecasts = list(
            forecasts_col.find(query)
            .sort("date", ASCENDING)
            .limit(horizon)
        )
        
        if not forecasts:
            logger.warning(f"No forecasts found for region {region_id}")
            return {
                "region_id": region_id,
                "horizon": horizon,
                "mae": None,
                "mape": None,
                "points_compared": 0,
                "evaluated_at": datetime.utcnow().isoformat(),
                "model_version": "naive_v1",
                "error": "No forecasts found for this region",
            }
        
        # Get model version from first forecast
        model_version = forecasts[0].get("model_version", "naive_v1")
        
        # Collect actual values and predictions
        errors = []
        mape_values = []
        compared_dates = []
        
        for forecast in forecasts:
            forecast_date = forecast.get("date")
            pred_mean = forecast.get("pred_mean", 0)
            
            # Find actual case data for this date
            actual_case = cases_col.find_one({
                "region_id": region_id,
                "date": forecast_date
            })
            
            if actual_case:
                actual_confirmed = float(actual_case.get("confirmed", 0))
                
                # Calculate absolute error for MAE
                abs_error = abs(actual_confirmed - pred_mean)
                errors.append(abs_error)
                
                # Calculate MAPE
                mape_val = safe_mape(actual_confirmed, pred_mean)
                if mape_val is not None:
                    mape_values.append(mape_val)
                
                compared_dates.append(forecast_date)
        
        # Compute metrics
        points_compared = len(errors)
        mae = sum(errors) / points_compared if points_compared > 0 else None
        mape = sum(mape_values) / len(mape_values) if mape_values else None
        
        result = {
            "region_id": region_id,
            "horizon": horizon,
            "mae": round(mae, 2) if mae is not None else None,
            "mape": round(mape, 2) if mape is not None else None,
            "points_compared": points_compared,
            "evaluated_at": datetime.utcnow().isoformat(),
            "model_version": model_version,
            "dates_evaluated": compared_dates,
        }
        
        logger.info(
            f"Evaluated forecast for {region_id}: "
            f"MAE={result['mae']}, MAPE={result['mape']}, points={points_compared}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error evaluating forecast for {region_id}: {e}")
        return {
            "region_id": region_id,
            "horizon": horizon,
            "mae": None,
            "mape": None,
            "points_compared": 0,
            "evaluated_at": datetime.utcnow().isoformat(),
            "model_version": "unknown",
            "error": str(e),
        }
