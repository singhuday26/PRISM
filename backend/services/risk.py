from __future__ import annotations

import logging
from datetime import datetime
from statistics import mean, stdev
from typing import Dict, List, Optional, Tuple

from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection

from backend.db import get_db
from backend.utils.climate import calculate_weather_aware_risk

logger = logging.getLogger(__name__)


def clip01(x: float) -> float:
    """Clip value to [0, 1] range."""
    return max(0.0, min(1.0, x))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0 or abs(denominator) < 1e-10:
        return default
    return numerator / denominator


def _series_std(values: List[float]) -> float:
    """Calculate standard deviation safely."""
    if len(values) < 2:
        return 0.0
    try:
        return float(stdev(values))
    except Exception as e:
        logger.warning(f"Error calculating stdev: {e}")
        return 0.0


def compute_region_metrics(
    region_id: str, target_date: str, cases_col: Collection, disease: Optional[str] = None
) -> Optional[Dict]:
    """Compute metrics for a region based on historical case data."""
    try:
        query = {"region_id": region_id}
        if target_date:
            query["date"] = {"$lte": target_date}
        if disease:
            query["disease"] = disease

        docs_desc = list(cases_col.find(query).sort("date", DESCENDING).limit(7))
        if not docs_desc:
            logger.debug(f"No data found for region {region_id}")
            return None

        docs = list(reversed(docs_desc))  # ascending by date

        confirmed_series = [int(doc.get("confirmed", 0) or 0) for doc in docs]
        deaths_series = [int(doc.get("deaths", 0) or 0) for doc in docs]

        today_confirmed = confirmed_series[-1]
        past_confirmed = confirmed_series[0]
        today_deaths = deaths_series[-1]

        # Use safe division to prevent division by zero
        growth_rate = safe_divide(today_confirmed - past_confirmed, max(past_confirmed, 1))
        death_ratio = safe_divide(today_deaths, max(today_confirmed, 1))

        mean_confirmed = mean(confirmed_series) if confirmed_series else 0.0
        volatility_norm = safe_divide(_series_std(confirmed_series), max(mean_confirmed, 1))

        metrics = {
            "region_id": region_id,
            "window_size": len(docs),
            "today_confirmed": today_confirmed,
            "past_confirmed": past_confirmed,
            "growth_rate": growth_rate,
            "death_ratio": death_ratio,
            "volatility_norm": volatility_norm,
        }
        return metrics
    except Exception as e:
        logger.error(f"Error computing metrics for region {region_id}: {e}")
        return None


def compute_risk_score(metrics: Dict, target_date: str = None, region_id: str = None, 
                       use_climate_boost: bool = True) -> Tuple[float, str, List[str], Dict]:
    """
    Compute risk score with optional weather-aware climate boost.
    
    Args:
        metrics: Region metrics dictionary
        target_date: Date for climate context (ISO format)
        region_id: Region identifier for regional climate adjustments
        use_climate_boost: Whether to apply climate-based risk multiplier
        
    Returns:
        Tuple of (score, risk_level, drivers, climate_info)
    """
    growth_rate = float(metrics.get("growth_rate", 0.0))
    volatility_norm = float(metrics.get("volatility_norm", 0.0))
    death_ratio = float(metrics.get("death_ratio", 0.0))

    # Base risk calculation (unchanged)
    base_score = (
        0.65 * clip01(growth_rate)
        + 0.25 * clip01(volatility_norm * 2)
        + 0.10 * clip01(death_ratio * 50)
    )

    drivers: List[str] = []
    climate_info: Dict = {}
    
    # Apply weather-aware climate boost
    if use_climate_boost and target_date:
        adjusted_score, climate_explanation, climate_context = calculate_weather_aware_risk(
            base_score, target_date, region_id
        )
        climate_info = {
            "base_risk": base_score,
            "climate_multiplier": climate_context.get("climate_multiplier", 1.0),
            "adjusted_risk": adjusted_score,
            "explanation": climate_explanation,
            "season": climate_context.get("season", "unknown"),
            "is_monsoon": climate_context.get("is_monsoon", False)
        }
        
        # Add climate driver if significant boost/reduction
        boost_pct = ((adjusted_score - base_score) / base_score * 100) if base_score > 0 else 0
        if abs(boost_pct) > 10:
            drivers.append(climate_explanation)
        
        score = adjusted_score
    else:
        score = base_score
        climate_info = {"base_risk": base_score, "climate_boost_enabled": False}
    
    # Existing risk drivers
    if growth_rate >= 0.30:
        drivers.append("High 7-day growth")
    if volatility_norm >= 0.15:
        drivers.append("High volatility")
    if death_ratio >= 0.02:
        drivers.append("High death ratio")
    if not drivers:
        drivers.append("Stable trend")

    if score >= 0.70:
        risk_level = "HIGH"
    elif score >= 0.40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return score, risk_level, drivers, climate_info


def compute_risk_scores(target_date: Optional[str] = None, disease: Optional[str] = None, 
                       use_climate_boost: bool = True) -> Tuple[str, List[Dict]]:
    """
    Compute risk scores for all regions, optionally filtered by disease.
    
    Args:
        target_date: Date to compute risk for (ISO format)
        disease: Optional disease filter
        use_climate_boost: Whether to apply weather-aware climate multipliers (default: True)
    
    Returns:
        Tuple of (target_date, list of risk score records)
    """
    try:
        db = get_db()
        cases_col = db["cases_daily"]
        regions_col = db["regions"]
        risk_col = db["risk_scores"]

        # Build query filter
        case_filter = {}
        if disease:
            case_filter["disease"] = disease
        
        if target_date is None:
            latest_case = cases_col.find_one(case_filter, sort=[("date", DESCENDING)])
            if not latest_case:
                logger.warning(f"No cases found in database{' for disease: ' + disease if disease else ''}")
                return "", []
            target_date = latest_case["date"]

        disease_info = f" for disease: {disease}" if disease else ""
        climate_info = " with climate boost" if use_climate_boost else ""
        logger.info(f"Computing risk scores for date: {target_date}{disease_info}{climate_info}")
        
        region_filter = {"disease": disease} if disease else {}
        regions = list(regions_col.find(region_filter, {"region_id": 1, "_id": 0}))
        logger.info(f"Processing {len(regions)} regions")
        
        results: List[Dict] = []
        skipped = 0

        for region in regions:
            region_id = region["region_id"]
            metrics = compute_region_metrics(region_id, target_date, cases_col, disease)
            if not metrics:
                skipped += 1
                continue

            score, risk_level, drivers, climate_data = compute_risk_score(
                metrics, target_date, region_id, use_climate_boost
            )
            
            doc = {
                "region_id": region_id,
                "date": target_date,
                "risk_score": score,
                "risk_level": risk_level,
                "drivers": drivers,
                "metrics": metrics,
                "climate_info": climate_data,  # NEW: Climate context
                "updated_at": datetime.utcnow(),
            }
            if disease:
                doc["disease"] = disease

            # Build upsert filter including disease for proper isolation
            upsert_filter = {"region_id": region_id, "date": target_date}
            if disease:
                upsert_filter["disease"] = disease

            risk_col.update_one(
                upsert_filter, {"$set": doc}, upsert=True
            )
            results.append(doc)

        if skipped > 0:
            logger.warning(f"Skipped {skipped} regions due to missing data")
        
        results.sort(key=lambda x: x.get("risk_score", 0.0), reverse=True)
        logger.info(f"Computed {len(results)} risk scores")
        return target_date, results
    except Exception as e:
        logger.error(f"Error computing risk scores: {e}")
        raise
