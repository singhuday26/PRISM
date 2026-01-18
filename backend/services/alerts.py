from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from pymongo import DESCENDING

from backend.config import get_settings
from backend.db import get_db

logger = logging.getLogger(__name__)


def generate_alerts(target_date: Optional[str] = None, disease: Optional[str] = None) -> Tuple[str, List[dict]]:
    """
    Generate alerts from risk_scores for a given date (default latest), optionally filtered by disease.
    
    Returns:
        Tuple of (resolved_date, list of alert records)
    """
    try:
        settings = get_settings()
        db = get_db()
        risk_col = db["risk_scores"]
        alerts_col = db["alerts"]

        # Build filter for disease
        risk_filter = {}
        if disease:
            risk_filter["disease"] = disease

        # Determine target date from latest risk score if not provided
        if target_date is None:
            latest_risk = risk_col.find_one(risk_filter, sort=[("date", DESCENDING)])
            if not latest_risk:
                logger.warning(f"No risk scores found for alert generation{' for disease: ' + disease if disease else ''}")
                return "", []
            target_date = latest_risk["date"]

        disease_info = f" for disease: {disease}" if disease else ""
        logger.info(f"Generating alerts for date: {target_date}{disease_info}")
        
        risk_filter["date"] = target_date
        risk_docs = list(
            risk_col.find(risk_filter, {"_id": 0}).sort("risk_score", DESCENDING)
        )
        
        if not risk_docs:
            logger.warning(f"No risk scores found for date {target_date}")
            return target_date, []

        threshold = float(getattr(settings, "risk_high_threshold", 0.7))
        logger.info(f"Using threshold: {threshold}")
        alerts: List[dict] = []

        for rd in risk_docs:
            score = float(rd.get("risk_score", 0.0) or 0.0)
            if score < threshold:
                continue

            alert = {
                "region_id": rd.get("region_id"),
                "date": target_date,
                "risk_score": score,
                "risk_level": rd.get("risk_level"),
                "reason": f"Risk score {score:.2f} >= threshold {threshold:.2f}",
                "created_at": datetime.utcnow(),
            }
            if disease:
                alert["disease"] = disease
            alerts_col.update_one(
                {"region_id": alert["region_id"], "date": target_date, "reason": alert["reason"]},
                {"$set": alert},
                upsert=True,
            )
            alerts.append(alert)

        alerts.sort(key=lambda x: x.get("risk_score", 0.0), reverse=True)
        logger.info(f"Generated {len(alerts)} alerts")
        return target_date, alerts
    except Exception as e:
        logger.error(f"Error generating alerts: {e}")
        raise
