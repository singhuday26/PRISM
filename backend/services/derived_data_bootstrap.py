"""Helpers to backfill derived collections when deployment DB has only raw case data."""
from __future__ import annotations

import logging
from threading import Lock
from typing import Optional

from backend.db import get_db
from backend.services.alerts import generate_alerts
from backend.services.forecasting import generate_forecasts
from backend.services.risk import compute_risk_scores

logger = logging.getLogger(__name__)

_LOCK_GUARD = Lock()
_DISEASE_LOCKS: dict[str, Lock] = {}


def _normalize_disease(disease: Optional[str]) -> Optional[str]:
    if not disease:
        return None
    normalized = disease.strip().upper()
    return normalized or None


def _get_disease_lock(disease: str) -> Lock:
    with _LOCK_GUARD:
        lock = _DISEASE_LOCKS.get(disease)
        if lock is None:
            lock = Lock()
            _DISEASE_LOCKS[disease] = lock
        return lock


def ensure_derived_data_for_disease(
    disease: Optional[str],
    *,
    forecast_horizon: int = 7,
    forecast_granularity: str = "monthly",
) -> dict:
    """
    Ensure risk_scores, alerts, and forecasts exist for a disease.

    This is used by read endpoints to self-heal fresh deployments where
    ``cases_daily`` has been seeded but derived collections are still empty.
    """
    normalized = _normalize_disease(disease)
    if not normalized:
        return {
            "disease": None,
            "cases_available": False,
            "risk_bootstrapped": False,
            "alerts_bootstrapped": False,
            "forecasts_bootstrapped": False,
        }

    lock = _get_disease_lock(normalized)
    with lock:
        db = get_db()

        case_filter = {"disease": normalized}
        if db["cases_daily"].find_one(case_filter, {"_id": 1}) is None:
            logger.warning(
                "Skipping derived bootstrap for %s: no matching case data",
                normalized,
            )
            return {
                "disease": normalized,
                "cases_available": False,
                "risk_bootstrapped": False,
                "alerts_bootstrapped": False,
                "forecasts_bootstrapped": False,
            }

        risk_bootstrapped = False
        alerts_bootstrapped = False
        forecasts_bootstrapped = False

        if db["risk_scores"].find_one({"disease": normalized}, {"_id": 1}) is None:
            _, risk_rows = compute_risk_scores(target_date=None, disease=normalized)
            risk_bootstrapped = len(risk_rows) > 0
            logger.info(
                "Bootstrapped risk scores for %s: %d rows",
                normalized,
                len(risk_rows),
            )

        if db["alerts"].find_one({"disease": normalized}, {"_id": 1}) is None:
            _, alert_rows = generate_alerts(target_date=None, disease=normalized)
            alerts_bootstrapped = len(alert_rows) > 0
            logger.info(
                "Bootstrapped alerts for %s: %d rows",
                normalized,
                len(alert_rows),
            )

        if db["forecasts_daily"].find_one({"disease": normalized}, {"_id": 1}) is None:
            _, forecast_rows = generate_forecasts(
                target_date=None,
                horizon=max(forecast_horizon, 7),
                disease=normalized,
                granularity=forecast_granularity,
            )
            forecasts_bootstrapped = len(forecast_rows) > 0
            logger.info(
                "Bootstrapped forecasts for %s: %d rows",
                normalized,
                len(forecast_rows),
            )

        return {
            "disease": normalized,
            "cases_available": True,
            "risk_bootstrapped": risk_bootstrapped,
            "alerts_bootstrapped": alerts_bootstrapped,
            "forecasts_bootstrapped": forecasts_bootstrapped,
        }
