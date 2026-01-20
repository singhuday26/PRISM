"""
ARIMA-based forecasting service for PRISM.

Provides statistical time-series forecasting using ARIMA/SARIMA models
as an upgrade from the naive baseline forecasting.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple, Literal
from statistics import mean, stdev

import numpy as np
from pymongo import DESCENDING

from backend.db import get_db

logger = logging.getLogger(__name__)

MODEL_VERSION_ARIMA = "arima_v1"
MODEL_VERSION_SARIMA = "sarima_v1"

GranularityType = Literal["yearly", "monthly", "weekly"]

# Lookback configuration - ARIMA needs more history
ARIMA_LOOKBACK_CONFIG = {
    "yearly": 5,     # 5 years of history
    "monthly": 24,   # 24 months of history
    "weekly": 52,    # 52 weeks of history
}

# Seasonal periods
SEASONAL_PERIODS = {
    "yearly": 1,     # No seasonality for yearly
    "monthly": 12,   # 12-month seasonality
    "weekly": 52,    # 52-week seasonality
}


def _fit_arima_model(
    series: List[float],
    seasonal: bool = False,
    seasonal_period: int = 12
) -> Optional[object]:
    """
    Fit ARIMA or SARIMA model to time series.
    
    Args:
        series: Historical time series data
        seasonal: Whether to use seasonal ARIMA
        seasonal_period: Period for seasonality
        
    Returns:
        Fitted model or None if fitting fails
    """
    try:
        # Lazy import to avoid loading until needed
        from pmdarima import auto_arima
        
        if len(series) < 10:
            logger.warning(f"Insufficient data for ARIMA: {len(series)} points")
            return None
        
        # Convert to numpy array
        y = np.array(series, dtype=float)
        
        # Handle any NaN/Inf values
        y = np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Fit auto_arima
        model = auto_arima(
            y,
            start_p=0, max_p=3,
            start_q=0, max_q=3,
            d=None,  # Auto-determine differencing
            seasonal=seasonal,
            m=seasonal_period if seasonal else 1,
            start_P=0, max_P=2,
            start_Q=0, max_Q=2,
            D=None if seasonal else 0,
            trace=False,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True,
            n_fits=10,  # Limit fits for speed
        )
        
        logger.debug(f"Fitted ARIMA model: {model.order}")
        return model
        
    except ImportError:
        logger.error("pmdarima not installed. Run: pip install pmdarima")
        return None
    except Exception as e:
        logger.error(f"Error fitting ARIMA model: {e}")
        return None


def _generate_arima_predictions(
    model,
    horizon: int,
    confidence_level: float = 0.95
) -> Tuple[List[float], List[float], List[float]]:
    """
    Generate predictions from fitted ARIMA model.
    
    Args:
        model: Fitted ARIMA model
        horizon: Number of periods to forecast
        confidence_level: Confidence level for intervals
        
    Returns:
        Tuple of (predictions, lower_bounds, upper_bounds)
    """
    try:
        # Generate forecast with confidence intervals
        forecast, conf_int = model.predict(
            n_periods=horizon,
            return_conf_int=True,
            alpha=1 - confidence_level
        )
        
        predictions = forecast.tolist()
        lower_bounds = conf_int[:, 0].tolist()
        upper_bounds = conf_int[:, 1].tolist()
        
        # Ensure non-negative predictions
        predictions = [max(0, p) for p in predictions]
        lower_bounds = [max(0, lb) for lb in lower_bounds]
        upper_bounds = [max(0, ub) for ub in upper_bounds]
        
        return predictions, lower_bounds, upper_bounds
        
    except Exception as e:
        logger.error(f"Error generating ARIMA predictions: {e}")
        return [], [], []


def generate_arima_forecast(
    region_id: str,
    target_date: Optional[str] = None,
    horizon: int = 7,
    run_ts: Optional[datetime] = None,
    disease: Optional[str] = None,
    granularity: GranularityType = "monthly",
    use_seasonal: bool = True
) -> List[Dict]:
    """
    Generate ARIMA/SARIMA forecast for a single region.
    
    Args:
        region_id: Region identifier
        target_date: Date to forecast from (ISO format)
        horizon: Number of periods to forecast ahead
        run_ts: Timestamp when forecast was generated
        disease: Filter by disease type
        granularity: Data granularity to use
        use_seasonal: Whether to use seasonal ARIMA (SARIMA)
        
    Returns:
        List of forecast records
    """
    try:
        db = get_db()
        cases_col = db["cases_daily"]
        forecasts_col = db["forecasts_daily"]
        
        # Build filter
        case_filter = {"region_id": region_id}
        if target_date:
            case_filter["date"] = {"$lte": target_date}
        if disease:
            case_filter["disease"] = disease
        if granularity == "yearly":
            case_filter["granularity"] = {"$exists": False}
        else:
            case_filter["granularity"] = granularity
        
        # Get historical data
        lookback = ARIMA_LOOKBACK_CONFIG.get(granularity, 24)
        historical_docs = list(
            cases_col.find(case_filter)
            .sort("date", DESCENDING)
            .limit(lookback)
        )
        
        if len(historical_docs) < 10:
            logger.warning(
                f"Insufficient data for ARIMA forecast in {region_id}: "
                f"{len(historical_docs)} records"
            )
            return []
        
        # Reverse to chronological order and extract series
        historical_docs.reverse()
        confirmed_series = [int(doc.get("confirmed", 0) or 0) for doc in historical_docs]
        
        # Resolve target date
        if not target_date:
            target_date = historical_docs[-1].get("date")
        
        # Fit ARIMA model
        seasonal_period = SEASONAL_PERIODS.get(granularity, 12)
        model = _fit_arima_model(
            confirmed_series,
            seasonal=use_seasonal and len(confirmed_series) >= seasonal_period * 2,
            seasonal_period=seasonal_period
        )
        
        if model is None:
            logger.warning(f"Could not fit ARIMA model for {region_id}")
            return []
        
        # Generate predictions
        predictions, lower_bounds, upper_bounds = _generate_arima_predictions(
            model, horizon
        )
        
        if not predictions:
            return []
        
        # Create forecast documents
        start = date.fromisoformat(target_date)
        run_ts = run_ts or datetime.utcnow()
        model_version = MODEL_VERSION_SARIMA if use_seasonal else MODEL_VERSION_ARIMA
        
        forecasts: List[Dict] = []
        for i, (pred, lower, upper) in enumerate(zip(predictions, lower_bounds, upper_bounds)):
            f_date = (start + timedelta(days=i + 1)).isoformat()
            doc = {
                "region_id": region_id,
                "date": f_date,
                "pred_mean": round(pred, 2),
                "pred_lower": round(lower, 2),
                "pred_upper": round(upper, 2),
                "model_version": model_version,
                "generated_at": run_ts,
                "source_granularity": granularity,
                "model_order": str(model.order) if hasattr(model, 'order') else None,
            }
            if disease:
                doc["disease"] = disease
                
            # Store in database
            forecasts_col.update_one(
                {"region_id": region_id, "date": f_date, "model_version": model_version},
                {"$set": doc},
                upsert=True,
            )
            forecasts.append(doc)
        
        logger.info(
            f"Generated ARIMA forecast for {region_id}: "
            f"{horizon} periods, model order {model.order}"
        )
        return forecasts
        
    except Exception as e:
        logger.error(f"Error generating ARIMA forecast for {region_id}: {e}")
        return []


def generate_arima_forecasts(
    target_date: Optional[str] = None,
    horizon: int = 7,
    disease: Optional[str] = None,
    granularity: GranularityType = "monthly",
    use_seasonal: bool = True
) -> Tuple[str, List[Dict]]:
    """
    Generate ARIMA forecasts for all regions.
    
    Args:
        target_date: Date to forecast from (ISO format)
        horizon: Number of periods to forecast ahead
        disease: Filter by disease type
        granularity: Data granularity to use
        use_seasonal: Whether to use seasonal ARIMA (SARIMA)
        
    Returns:
        Tuple of (resolved_date, list of forecast records)
    """
    try:
        db = get_db()
        cases_col = db["cases_daily"]
        regions_col = db["regions"]
        
        # Resolve target date
        case_filter = {}
        if disease:
            case_filter["disease"] = disease
        if granularity == "yearly":
            case_filter["granularity"] = {"$exists": False}
        else:
            case_filter["granularity"] = granularity
            
        latest = cases_col.find_one(case_filter, sort=[("date", DESCENDING)])
        resolved_date = target_date or (latest.get("date") if latest else None)
        
        if not resolved_date:
            logger.warning("No date available for ARIMA forecasts")
            return "", []
        
        # Get regions
        region_filter = {"disease": disease} if disease else {}
        regions = list(regions_col.find(region_filter, {"region_id": 1, "_id": 0}))
        
        logger.info(
            f"Generating ARIMA forecasts for {len(regions)} regions, "
            f"date: {resolved_date}, horizon: {horizon}"
        )
        
        run_ts = datetime.utcnow()
        results: List[Dict] = []
        successful = 0
        failed = 0
        
        for region in regions:
            region_id = region["region_id"]
            forecasts = generate_arima_forecast(
                region_id=region_id,
                target_date=resolved_date,
                horizon=horizon,
                run_ts=run_ts,
                disease=disease,
                granularity=granularity,
                use_seasonal=use_seasonal,
            )
            if forecasts:
                results.extend(forecasts)
                successful += 1
            else:
                failed += 1
        
        logger.info(
            f"ARIMA forecasting complete: {successful} regions successful, "
            f"{failed} failed, {len(results)} total records"
        )
        
        results.sort(key=lambda x: (x.get("region_id", ""), x.get("date", "")))
        return resolved_date, results
        
    except Exception as e:
        logger.error(f"Error generating ARIMA forecasts: {e}")
        raise


def compare_forecast_models(
    region_id: str,
    target_date: str,
    actual_values: List[float],
    disease: Optional[str] = None,
    granularity: GranularityType = "monthly"
) -> Dict:
    """
    Compare naive vs ARIMA forecasts against actual values.
    
    Args:
        region_id: Region to compare
        target_date: Base date for forecasts
        actual_values: Actual observed values
        disease: Disease filter
        granularity: Data granularity
        
    Returns:
        Dictionary with comparison metrics
    """
    from backend.services.forecasting import generate_forecast
    
    horizon = len(actual_values)
    
    # Generate naive forecast
    naive_forecasts = generate_forecast(
        region_id=region_id,
        target_date=target_date,
        horizon=horizon,
        disease=disease,
        granularity=granularity,
    )
    
    # Generate ARIMA forecast
    arima_forecasts = generate_arima_forecast(
        region_id=region_id,
        target_date=target_date,
        horizon=horizon,
        disease=disease,
        granularity=granularity,
    )
    
    def calculate_metrics(predictions: List[float], actuals: List[float]) -> Dict:
        """Calculate forecast accuracy metrics."""
        if not predictions or len(predictions) != len(actuals):
            return {"error": "Mismatched lengths"}
        
        errors = [abs(p - a) for p, a in zip(predictions, actuals)]
        pct_errors = [abs(p - a) / max(a, 1) * 100 for p, a in zip(predictions, actuals)]
        
        return {
            "mae": round(mean(errors), 2),
            "mape": round(mean(pct_errors), 2),
            "rmse": round((mean([e**2 for e in errors])) ** 0.5, 2),
        }
    
    naive_preds = [f["pred_mean"] for f in naive_forecasts]
    arima_preds = [f["pred_mean"] for f in arima_forecasts]
    
    return {
        "region_id": region_id,
        "date": target_date,
        "horizon": horizon,
        "naive": calculate_metrics(naive_preds, actual_values),
        "arima": calculate_metrics(arima_preds, actual_values),
        "actual_values": actual_values,
        "naive_predictions": naive_preds,
        "arima_predictions": arima_preds,
    }
