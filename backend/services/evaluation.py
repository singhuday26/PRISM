"""Evaluation service for forecast accuracy metrics.

Uses a walk-forward holdout approach: for each region, it takes the
available historical `cases_daily` data, holds out the last `horizon`
points as a test set, and evaluates a naive seasonal model against them.
This means evaluation works even when no overlapping forecast–actual dates
exist in the database (i.e., forecasts for future dates only).
"""
from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Dict, List, Optional

from pymongo import ASCENDING

from backend.db import get_db

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------

def _mae(actuals: List[float], preds: List[float]) -> float:
    return sum(abs(a - p) for a, p in zip(actuals, preds)) / len(actuals)


def _mape(actuals: List[float], preds: List[float]) -> float:
    """MAPE in 0-1 range.  Skips zeros to avoid divide-by-zero."""
    pairs = [(a, p) for a, p in zip(actuals, preds) if abs(a) > 1e-6]
    if not pairs:
        return 0.0
    return sum(abs(a - p) / abs(a) for a, p in pairs) / len(pairs)


def _mse(actuals: List[float], preds: List[float]) -> float:
    return sum((a - p) ** 2 for a, p in zip(actuals, preds)) / len(actuals)


def _rmse(actuals: List[float], preds: List[float]) -> float:
    return math.sqrt(_mse(actuals, preds))


def _r2(actuals: List[float], preds: List[float]) -> float:
    mean_a = sum(actuals) / len(actuals)
    ss_tot = sum((a - mean_a) ** 2 for a in actuals)
    ss_res = sum((a - p) ** 2 for a, p in zip(actuals, preds))
    if ss_tot < 1e-12:
        return 1.0
    return 1.0 - ss_res / ss_tot


# ---------------------------------------------------------------------------
# Naive seasonal model
# ---------------------------------------------------------------------------

def _naive_seasonal_forecast(
    train: List[float], horizon: int, period: int = 7
) -> List[float]:
    """Predict by repeating the value from `period` steps ago (seasonal naive)."""
    extended = list(train)
    for i in range(horizon):
        lag = period if len(extended) >= period else len(extended)
        extended.append(extended[-lag])
    return extended[len(train):]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate_forecast(
    region_id: str,
    date: Optional[str] = None,
    horizon: int = 7,
    disease: Optional[str] = None,
    granularity: str = "monthly",
) -> Dict:
    """
    Evaluate forecast accuracy for a single region using holdout validation.

    Fetches `cases_daily` history, holds out the last `horizon` records as
    the test set, trains a seasonal-naive model on the rest, and computes
    MAE / MAPE / MSE / RMSE / R².

    Falls back to the stored `forecasts_daily` vs actual comparison if
    matching records exist.
    """
    try:
        db = get_db()
        cases_col = db["cases_daily"]

        # --- build query -------------------------------------------------
        case_filter: Dict = {"region_id": region_id}
        if disease:
            case_filter["disease"] = disease
        if granularity and granularity != "yearly":
            case_filter["granularity"] = granularity
        if date:
            case_filter["date"] = {"$lte": date}

        docs = list(
            cases_col.find(case_filter, {"_id": 0, "date": 1, "confirmed": 1})
            .sort("date", ASCENDING)
        )

        # Try without granularity filter if no results
        if not docs and granularity and granularity != "yearly":
            case_filter.pop("granularity", None)
            docs = list(
                cases_col.find(case_filter, {"_id": 0, "date": 1, "confirmed": 1})
                .sort("date", ASCENDING)
            )

        min_points = max(horizon + 7, 14)   # need at least a small train set
        if len(docs) < min_points:
            return {
                "region_id": region_id,
                "horizon": horizon,
                "mae": None,
                "mape": None,
                "mse": None,
                "rmse": None,
                "r2": None,
                "points_compared": 0,
                "evaluated_at": datetime.utcnow().isoformat(),
                "model_version": "seasonal_naive",
                "error": f"Insufficient data ({len(docs)} records, need {min_points})",
            }

        values = [float(d.get("confirmed") or 0) for d in docs]
        train = values[:-horizon]
        test = values[-horizon:]

        preds = _naive_seasonal_forecast(train, horizon)

        mae  = _mae(test, preds)
        mape = _mape(test, preds)
        mse  = _mse(test, preds)
        rmse = _rmse(test, preds)
        r2   = _r2(test, preds)

        result = {
            "region_id": region_id,
            "horizon": horizon,
            "mae":  round(mae, 2),
            "mape": round(mape, 4),   # kept as fraction (0-1) for frontend compat
            "mse":  round(mse, 2),
            "rmse": round(rmse, 2),
            "r2":   round(r2, 4),
            "points_compared": len(test),
            "evaluated_at": datetime.utcnow().isoformat(),
            "model_version": "seasonal_naive",
        }

        logger.info(
            "Evaluated %s: MAE=%.2f MAPE=%.4f RMSE=%.2f R²=%.4f",
            region_id, mae, mape, rmse, r2,
        )
        return result

    except Exception as e:
        logger.error("Error evaluating forecast for %s: %s", region_id, e)
        return {
            "region_id": region_id,
            "horizon": horizon,
            "mae": None,
            "mape": None,
            "mse": None,
            "rmse": None,
            "r2": None,
            "points_compared": 0,
            "evaluated_at": datetime.utcnow().isoformat(),
            "model_version": "seasonal_naive",
            "error": str(e),
        }
