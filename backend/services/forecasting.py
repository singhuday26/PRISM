from __future__ import annotations

import logging
from datetime import datetime, timedelta, date
from statistics import mean
from typing import Dict, List, Optional, Tuple, Literal

from pymongo import DESCENDING

from backend.db import get_db

logger = logging.getLogger(__name__)
MODEL_VERSION = "naive_v2"  # Updated to v2 for granularity support

# Lookback configuration based on granularity
LOOKBACK_CONFIG = {
    "yearly": 3,    # 3 years of history
    "monthly": 6,   # 6 months of history
    "weekly": 12,   # 12 weeks of history
}

GranularityType = Literal["yearly", "monthly", "weekly"]


def _resolve_target_date(
    cases_col, 
    target_date: Optional[str], 
    disease: Optional[str] = None,
    granularity: Optional[GranularityType] = None
) -> Optional[str]:
    """Resolve target date to latest if not provided."""
    if target_date:
        return target_date
    
    case_filter = {}
    if disease:
        case_filter["disease"] = disease
    if granularity:
        if granularity == "yearly":
            case_filter["granularity"] = {"$exists": False}  # Original yearly data
        else:
            case_filter["granularity"] = granularity
    
    latest = cases_col.find_one(case_filter, sort=[("date", DESCENDING)])
    if not latest:
        logger.warning(
            f"No cases found in database"
            f"{' for disease: ' + disease if disease else ''}"
            f"{' with granularity: ' + granularity if granularity else ''}"
        )
        return None
    return latest.get("date")


def generate_forecast(
    region_id: str, 
    target_date: Optional[str] = None, 
    horizon: int = 7, 
    run_ts: Optional[datetime] = None, 
    disease: Optional[str] = None,
    granularity: GranularityType = "monthly"
) -> List[Dict]:
    """
    Generate naive forecast for a single region.
    
    Args:
        region_id: Region identifier
        target_date: Date to forecast from (ISO format)
        horizon: Number of days to forecast ahead
        run_ts: Timestamp when forecast was generated
        disease: Filter by disease type
        granularity: Data granularity to use ("yearly", "monthly", or "weekly")
                    Default is "monthly" for best balance of signal vs noise
    
    Returns:
        List of forecast records
    """
    try:
        db = get_db()
        cases_col = db["cases_daily"]
        forecasts_col = db["forecasts_daily"]

        target_date = _resolve_target_date(cases_col, target_date, disease, granularity)
        if not target_date:
            logger.warning(f"No target date available for region {region_id}")
            return []

        # Build filter with granularity support
        case_filter = {"region_id": region_id, "date": {"$lte": target_date}}
        if disease:
            case_filter["disease"] = disease
        if granularity == "yearly":
            case_filter["granularity"] = {"$exists": False}  # Original yearly data
        else:
            case_filter["granularity"] = granularity
        
        # Get lookback count based on granularity
        lookback = LOOKBACK_CONFIG.get(granularity, 6)
        
        last_docs = list(
            cases_col.find(case_filter)
            .sort("date", DESCENDING)
            .limit(lookback)
        )
        if not last_docs:
            logger.debug(
                f"No historical data for region {region_id} "
                f"with granularity {granularity}"
            )
            return []

        # Calculate mean from historical data
        confirmed_series = [int(doc.get("confirmed", 0) or 0) for doc in last_docs]
        pred_mean = mean(confirmed_series)
        pred_lower = pred_mean * 0.90
        pred_upper = pred_mean * 1.10

        start = date.fromisoformat(target_date)
        run_ts = run_ts or datetime.utcnow()

        forecasts: List[Dict] = []
        for day in range(1, horizon + 1):
            f_date = (start + timedelta(days=day)).isoformat()
            doc = {
                "region_id": region_id,
                "date": f_date,
                "pred_mean": pred_mean,
                "pred_lower": pred_lower,
                "pred_upper": pred_upper,
                "model_version": MODEL_VERSION,
                "generated_at": run_ts,
                "source_granularity": granularity,  # Track which data was used
            }
            if disease:
                doc["disease"] = disease
            forecasts_col.update_one(
                {"region_id": region_id, "date": f_date, "model_version": MODEL_VERSION},
                {"$set": doc},
                upsert=True,
            )
            forecasts.append(doc)

        return forecasts
    except Exception as e:
        logger.error(f"Error generating forecast for region {region_id}: {e}")
        return []


def generate_forecasts(
    target_date: Optional[str] = None, 
    horizon: int = 7, 
    disease: Optional[str] = None,
    granularity: GranularityType = "monthly"
) -> Tuple[str, List[Dict]]:
    """
    Generate forecasts for all regions, optionally filtered by disease.
    
    Args:
        target_date: Date to forecast from (ISO format)
        horizon: Number of days to forecast ahead
        disease: Filter by disease type
        granularity: Data granularity to use ("yearly", "monthly", or "weekly")
                    Default is "monthly" for optimal forecasting accuracy
    
    Returns:
        Tuple of (resolved_date, list of forecast records)
    """
    try:
        db = get_db()
        cases_col = db["cases_daily"]
        regions_col = db["regions"]

        resolved_date = _resolve_target_date(cases_col, target_date, disease, granularity)
        if not resolved_date:
            logger.warning(
                f"No date available for forecasts"
                f"{' for disease: ' + disease if disease else ''}"
                f"{' with granularity: ' + granularity if granularity else ''}"
            )
            return "", []

        disease_info = f" for disease: {disease}" if disease else ""
        logger.info(
            f"Generating forecasts for date: {resolved_date} with horizon {horizon}"
            f"{disease_info} using {granularity} data"
        )
        
        region_filter = {"disease": disease} if disease else {}
        regions = list(regions_col.find(region_filter, {"region_id": 1, "_id": 0}))
        logger.info(f"Processing {len(regions)} regions")
        
        run_ts = datetime.utcnow()
        results: List[Dict] = []
        skipped = 0

        for region in regions:
            region_id = region["region_id"]
            region_forecasts = generate_forecast(
                region_id, resolved_date, horizon, run_ts, disease, granularity
            )
            if not region_forecasts:
                skipped += 1
            results.extend(region_forecasts)

        if skipped > 0:
            logger.warning(f"Skipped {skipped} regions due to missing data")
        
        results.sort(key=lambda x: (x.get("region_id", ""), x.get("date", "")))
        logger.info(f"Generated {len(results)} forecast records using {granularity} data")
        return resolved_date, results
    except Exception as e:
        logger.error(f"Error generating forecasts: {e}")
        raise
