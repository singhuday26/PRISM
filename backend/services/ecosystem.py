"""Service layer for the Ecosystem Wing."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid

from backend.db import get_db
from backend.schemas.ecosystem import (
    AlertSeverity,
    CategorySummary,
    EcosystemSummary,
    Institution,
    InstitutionAlert,
    InstitutionType,
    OperationalStatus,
)

logger = logging.getLogger(__name__)

# Human-friendly labels for each type
TYPE_LABELS: Dict[str, str] = {
    "hospital": "Hospitals",
    "ambulance": "Ambulance Services",
    "fire_station": "Fire & Rescue",
    "lab": "Public Health Labs",
    "pharmacy": "Pharmacies & Supply",
    "district_admin": "District Administration",
    "police": "Police & Law Enforcement",
    "blood_bank": "Blood Banks",
    "wash": "Water & Sanitation",
    "ngo": "NGOs & Relief Orgs",
}

# Alert thresholds per institution type
_HOSPITAL_BED_THRESHOLD = 0.15       # alert when <15 % beds available
_HOSPITAL_ICU_THRESHOLD = 0.10       # alert when <10 % ICU available
_AMBULANCE_RESPONSE_THRESHOLD = 15.0  # alert when avg response > 15 min
_LAB_BACKLOG_THRESHOLD = 0.5         # alert when backlog > 50 % of capacity
_PHARMACY_STOCK_THRESHOLD = 30.0     # alert when stock health < 30 %
_BLOOD_EXPIRY_THRESHOLD = 10         # alert when >10 units expiring soon
_WASH_QUALITY_THRESHOLD = 50.0       # alert when water quality < 50


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_institutions(
    inst_type: Optional[str] = None,
    region_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
) -> List[dict]:
    """Return institutions from MongoDB, with optional filters."""
    db = get_db()
    query: Dict = {}
    if inst_type:
        query["type"] = inst_type
    if region_id:
        query["region_id"] = region_id.upper()
    if status:
        query["status"] = status

    projection = {"_id": 0}
    docs = list(
        db["institutions"]
        .find(query, projection)
        .sort("name", 1)
        .limit(limit)
    )

    # optional text search (name contains)
    if search:
        search_lower = search.lower()
        docs = [d for d in docs if search_lower in d.get("name", "").lower()]

    return docs


def get_institution_detail(institution_id: str) -> Optional[dict]:
    """Return a single institution by ID."""
    db = get_db()
    doc = db["institutions"].find_one(
        {"institution_id": institution_id}, {"_id": 0}
    )
    return doc


def compute_ecosystem_summary() -> dict:
    """Aggregate status across all institutions."""
    db = get_db()
    docs = list(db["institutions"].find({}, {"_id": 0}))

    if not docs:
        return EcosystemSummary().model_dump()

    # Group by type
    type_groups: Dict[str, List[dict]] = {}
    for d in docs:
        t = d.get("type", "unknown")
        type_groups.setdefault(t, []).append(d)

    categories: List[dict] = []
    total_health = 0.0

    for inst_type in InstitutionType:
        group = type_groups.get(inst_type.value, [])
        count = len(group)
        if count == 0:
            categories.append(
                CategorySummary(
                    type=inst_type,
                    label=TYPE_LABELS.get(inst_type.value, inst_type.value),
                ).model_dump()
            )
            continue

        statuses = [d.get("status", "operational") for d in group]
        health_scores = [d.get("health_score", 100) for d in group]
        avg_health = sum(health_scores) / count

        cat = CategorySummary(
            type=inst_type,
            label=TYPE_LABELS.get(inst_type.value, inst_type.value),
            count=count,
            operational=statuses.count("operational"),
            degraded=statuses.count("degraded"),
            critical=statuses.count("critical"),
            offline=statuses.count("offline"),
            avg_health_score=round(avg_health, 1),
        )
        categories.append(cat.model_dump())
        total_health += avg_health

    num_types_with_data = sum(1 for c in categories if c["count"] > 0)
    overall_health = round(total_health / num_types_with_data, 1) if num_types_with_data else 0.0

    alerts = generate_ecosystem_alerts(docs)

    summary = EcosystemSummary(
        total_institutions=len(docs),
        overall_health_score=overall_health,
        active_alerts=len(alerts),
        categories=categories,
    )

    return {"summary": summary.model_dump(), "alerts": [a.model_dump() for a in alerts]}


def generate_ecosystem_alerts(docs: List[dict]) -> List[InstitutionAlert]:
    """Generate threshold-based alerts across institutions."""
    alerts: List[InstitutionAlert] = []

    for d in docs:
        inst_id = d.get("institution_id", "")
        inst_name = d.get("name", "Unknown")
        inst_type = d.get("type", "hospital")
        region = d.get("region_id", "")
        detail = d.get("status_detail") or {}

        # Offline check (any type)
        if d.get("status") == "offline":
            alerts.append(InstitutionAlert(
                alert_id=str(uuid.uuid4())[:8],
                institution_id=inst_id,
                institution_name=inst_name,
                institution_type=inst_type,
                region_id=region,
                severity=AlertSeverity.CRITICAL,
                message=f"{inst_name} is OFFLINE",
                timestamp=_now_iso(),
            ))
            continue

        # Hospital checks
        if inst_type == "hospital":
            beds_total = detail.get("beds_total", 1)
            beds_avail = detail.get("beds_available", 0)
            if beds_total > 0 and (beds_avail / beds_total) < _HOSPITAL_BED_THRESHOLD:
                alerts.append(InstitutionAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    institution_id=inst_id,
                    institution_name=inst_name,
                    institution_type=inst_type,
                    region_id=region,
                    severity=AlertSeverity.HIGH,
                    message=f"Only {beds_avail}/{beds_total} beds available",
                    timestamp=_now_iso(),
                ))
            icu_total = detail.get("icu_total", 1)
            icu_avail = detail.get("icu_available", 0)
            if icu_total > 0 and (icu_avail / icu_total) < _HOSPITAL_ICU_THRESHOLD:
                alerts.append(InstitutionAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    institution_id=inst_id,
                    institution_name=inst_name,
                    institution_type=inst_type,
                    region_id=region,
                    severity=AlertSeverity.CRITICAL,
                    message=f"ICU near capacity: {icu_avail}/{icu_total} available",
                    timestamp=_now_iso(),
                ))

        # Ambulance checks
        elif inst_type == "ambulance":
            avg_resp = detail.get("avg_response_min", 0)
            if avg_resp > _AMBULANCE_RESPONSE_THRESHOLD:
                alerts.append(InstitutionAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    institution_id=inst_id,
                    institution_name=inst_name,
                    institution_type=inst_type,
                    region_id=region,
                    severity=AlertSeverity.MEDIUM,
                    message=f"Avg response time {avg_resp:.0f} min (threshold {_AMBULANCE_RESPONSE_THRESHOLD})",
                    timestamp=_now_iso(),
                ))

        # Lab checks
        elif inst_type == "lab":
            capacity = detail.get("daily_capacity", 1)
            backlog = detail.get("backlog", 0)
            if capacity > 0 and (backlog / capacity) > _LAB_BACKLOG_THRESHOLD:
                alerts.append(InstitutionAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    institution_id=inst_id,
                    institution_name=inst_name,
                    institution_type=inst_type,
                    region_id=region,
                    severity=AlertSeverity.HIGH,
                    message=f"Testing backlog {backlog} (capacity {capacity}/day)",
                    timestamp=_now_iso(),
                ))

        # Pharmacy checks
        elif inst_type == "pharmacy":
            stock_pct = detail.get("stock_health_pct", 100)
            if stock_pct < _PHARMACY_STOCK_THRESHOLD:
                alerts.append(InstitutionAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    institution_id=inst_id,
                    institution_name=inst_name,
                    institution_type=inst_type,
                    region_id=region,
                    severity=AlertSeverity.HIGH,
                    message=f"Critical drug stock at {stock_pct:.0f}%",
                    timestamp=_now_iso(),
                ))

        # Blood bank checks
        elif inst_type == "blood_bank":
            expiring = detail.get("units_expiring_soon", 0)
            if expiring > _BLOOD_EXPIRY_THRESHOLD:
                alerts.append(InstitutionAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    institution_id=inst_id,
                    institution_name=inst_name,
                    institution_type=inst_type,
                    region_id=region,
                    severity=AlertSeverity.MEDIUM,
                    message=f"{expiring} blood units expiring soon",
                    timestamp=_now_iso(),
                ))

        # WASH checks
        elif inst_type == "wash":
            wqi = detail.get("water_quality_index", 100)
            if wqi < _WASH_QUALITY_THRESHOLD:
                alerts.append(InstitutionAlert(
                    alert_id=str(uuid.uuid4())[:8],
                    institution_id=inst_id,
                    institution_name=inst_name,
                    institution_type=inst_type,
                    region_id=region,
                    severity=AlertSeverity.HIGH,
                    message=f"Water quality index {wqi:.0f}/100 — below safe threshold",
                    timestamp=_now_iso(),
                ))

    # Sort: CRITICAL first
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    alerts.sort(key=lambda a: severity_order.get(a.severity, 9))

    return alerts
