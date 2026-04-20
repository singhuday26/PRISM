import hashlib
import logging
import math
import random
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from pymongo import DESCENDING

from backend.db import get_db
from backend.schemas.responses import (
    ResourceConfig,
    ResourceConfigParams,
    ResourceDemand,
    ResourcePredictionResponse,
)

logger = logging.getLogger(__name__)


class ResourceService:
    def __init__(self):
        self.db = get_db()
        self.config_col = self.db["disease_config"]
        self.forecasts_col = self.db["forecasts_daily"]
        self.cases_col = self.db["cases_daily"]
        self.resources_col = self.db["resources_daily"]
        self.regions_col = self.db["regions"]

    def get_config(self, disease: str) -> ResourceConfig:
        """Get resource configuration for a disease."""
        disease_key = str(disease or "").strip().lower()
        doc = self.config_col.find_one({"_id": disease_key})

        if not doc:
            doc = self.config_col.find_one({"name": {"$regex": f"^{re.escape(disease)}$", "$options": "i"}})

        if not doc:
            logger.warning("No resource config found for %s, using defaults", disease)
            return ResourceConfig(
                disease=disease.upper(),
                resource_params=ResourceConfigParams(
                    hospitalization_rate=0.12,
                    icu_rate=0.02,
                    avg_stay_days=5,
                    nurse_ratio=0.15,
                    oxygen_rate=0.1,
                ),
            )

        params = doc.get("resource_params") or {}
        if "oxygen_rate" not in params:
            params["oxygen_rate"] = 0.1
        if "nurse_ratio" not in params:
            params["nurse_ratio"] = 0.15

        return ResourceConfig(
            disease=str(doc.get("name") or disease).upper(),
            resource_params=ResourceConfigParams(**params),
        )

    def set_config(self, config: ResourceConfig) -> None:
        """Update resource configuration."""
        self.config_col.update_one(
            {"_id": config.disease.lower()},
            {
                "$set": {
                    "name": config.disease.upper(),
                    "resource_params": config.resource_params.model_dump(),
                }
            },
            upsert=True,
        )

    def _disease_variants(self, disease: str) -> List[str]:
        token = str(disease or "").strip()
        return list({token.upper(), token.lower(), token.title()})

    def _normalize_region_token(self, value: str) -> str:
        token = str(value or "").strip()
        if not token:
            return ""
        if token.upper().startswith("IN-"):
            return token.upper()
        if re.fullmatch(r"[A-Za-z]{2}", token):
            return f"IN-{token.upper()}"
        return token.upper()

    def _resolve_region(self, region_ref: str) -> Dict[str, Any]:
        """Resolve region input (ID or name) to canonical region metadata."""
        raw_value = str(region_ref or "").strip()
        if not raw_value:
            return {"region_id": "UNKNOWN", "region_name": "Unknown", "population": 1_000_000}

        normalized_id = self._normalize_region_token(raw_value)
        projection = {"_id": 0, "region_id": 1, "region_name": 1, "population": 1}

        region_doc = self.regions_col.find_one({"region_id": normalized_id}, projection)
        if not region_doc:
            region_doc = self.regions_col.find_one(
                {"region_name": {"$regex": f"^{re.escape(raw_value)}$", "$options": "i"}},
                projection,
            )
        if not region_doc:
            region_doc = self.resources_col.find_one({"region_id": normalized_id}, projection)
        if not region_doc:
            region_doc = self.resources_col.find_one(
                {"region_name": {"$regex": f"^{re.escape(raw_value)}$", "$options": "i"}},
                projection,
            )

        if region_doc:
            region_id = str(region_doc.get("region_id") or normalized_id).upper()
            region_name = str(region_doc.get("region_name") or raw_value)
            population = int(region_doc.get("population") or 1_000_000)
            return {"region_id": region_id, "region_name": region_name, "population": population}

        logger.warning("Region '%s' not found in regions/resources collections; using inferred defaults", region_ref)
        inferred_name = raw_value if "-" not in raw_value else raw_value.upper()
        return {
            "region_id": normalized_id,
            "region_name": inferred_name,
            "population": 1_000_000,
        }

    def _extract_count(self, value: Any) -> int:
        try:
            if value is None:
                return 0
            if isinstance(value, bool):
                return 0
            if isinstance(value, (int, float)):
                return max(0, int(value))
            if isinstance(value, str):
                parsed = float(value.strip())
                return max(0, int(parsed))
        except (TypeError, ValueError):
            return 0
        return 0

    def _extract_total_occupied(self, block: Any) -> Tuple[int, int]:
        """Extract total and occupied from flexible nested resource fields."""
        if isinstance(block, dict):
            total = self._extract_count(
                block.get("total")
                or block.get("capacity")
                or block.get("max")
                or block.get("count")
            )
            occupied = self._extract_count(
                block.get("occupied")
                or block.get("in_use")
                or block.get("used")
                or block.get("utilized")
            )
            if not occupied:
                maybe_available = self._extract_count(block.get("available"))
                if total and maybe_available <= total:
                    occupied = max(0, total - maybe_available)
            return total, min(occupied, total) if total else occupied

        scalar = self._extract_count(block)
        return scalar, 0

    def _baseline_active_cases(self, population: int, disease: str) -> int:
        """Compute realistic lower-bound active cases for state-level planning."""
        normalized = str(disease or "").strip().upper()
        disease_floor_rate = {
            "DENGUE": 0.0009,
            "MALARIA": 0.0007,
            "CHIKUNGUNYA": 0.00045,
            "COVID": 0.0012,
            "COVID-19": 0.0012,
        }
        base_rate = disease_floor_rate.get(normalized, 0.0006)
        return max(1500, int(population * base_rate))

    def _safe_ratio(self, numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return max(0.0, float(numerator) / float(denominator))

    def _classify_level(self, urgency_score: float) -> str:
        if urgency_score >= 0.9:
            return "CRITICAL"
        if urgency_score >= 0.75:
            return "WARNING"
        return "SAFE"

    def _estimate_active_cases(
        self,
        region_id: str,
        target_date: str,
        disease: str,
        avg_stay_days: int,
    ) -> int:
        """Estimate active cases by summing recent confirmed/predicted daily values."""
        target_dt = date.fromisoformat(target_date)
        stay_days = max(1, int(avg_stay_days or 1))
        start_dt = target_dt - timedelta(days=stay_days - 1)
        start_date = start_dt.isoformat()
        disease_filter = {"$in": self._disease_variants(disease)}

        daily_counts: Dict[str, int] = {}

        hist_cursor = self.cases_col.find(
            {
                "region_id": region_id,
                "disease": disease_filter,
                "date": {"$gte": start_date, "$lte": target_date},
            },
            {"date": 1, "confirmed": 1, "cases": 1},
        )
        for doc in hist_cursor:
            day = str(doc.get("date") or "")
            if not day:
                continue
            daily_counts[day] = self._extract_count(doc.get("confirmed") or doc.get("cases"))

        forecast_cursor = self.forecasts_col.find(
            {
                "region_id": region_id,
                "disease": disease_filter,
                "date": {"$gte": start_date, "$lte": target_date},
            },
            {"date": 1, "cases": 1, "pred_mean": 1},
        )
        for doc in forecast_cursor:
            day = str(doc.get("date") or "")
            if not day or day in daily_counts:
                continue
            daily_counts[day] = self._extract_count(doc.get("cases") or doc.get("pred_mean"))

        if not daily_counts:
            fallback_docs = list(
                self.cases_col.find(
                    {"region_id": region_id, "disease": disease_filter},
                    {"confirmed": 1, "cases": 1, "date": 1},
                )
                .sort("date", DESCENDING)
                .limit(stay_days)
            )
            for doc in fallback_docs:
                day = str(doc.get("date") or "")
                if not day:
                    continue
                daily_counts[day] = self._extract_count(doc.get("confirmed") or doc.get("cases"))

        total_active = int(sum(daily_counts.values()))
        if total_active <= 0:
            logger.warning(
                "No case history found for region=%s disease=%s window=%s..%s",
                region_id,
                disease,
                start_date,
                target_date,
            )
        return max(0, total_active)

    def _build_synthetic_resource_doc(
        self,
        region_meta: Dict[str, Any],
        disease: str,
        target_date: str,
        active_cases: int,
    ) -> Dict[str, Any]:
        """Generate realistic per-region resources and persist for future requests."""
        region_id = str(region_meta.get("region_id") or "UNKNOWN").upper()
        region_name = str(region_meta.get("region_name") or region_id)
        population = max(100_000, int(region_meta.get("population") or 1_000_000))

        seed_key = f"{region_id}:{disease}:{target_date}"
        seed = int(hashlib.md5(seed_key.encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(seed)

        general_total = max(1200, int(population / 1800) + rng.randint(-120, 180))
        icu_total = max(140, int(general_total * (0.11 + rng.uniform(-0.01, 0.03))))
        vent_total = max(90, int(icu_total * (0.62 + rng.uniform(-0.04, 0.06))))

        pressure = min(0.25, active_cases / max(1.0, population / 1300))
        general_occ_ratio = min(0.95, max(0.58, 0.66 + pressure + rng.uniform(-0.03, 0.05)))
        icu_occ_ratio = min(0.97, max(0.56, 0.64 + pressure * 1.4 + rng.uniform(-0.03, 0.05)))

        general_occ = int(general_total * general_occ_ratio)
        icu_occ = int(icu_total * icu_occ_ratio)
        vent_occ = min(vent_total, int(vent_total * min(0.95, icu_occ_ratio + 0.05)))

        nurses_on_duty = max(320, int((general_occ + icu_occ) * (0.56 + rng.uniform(-0.03, 0.05))))
        oxygen_stock = max(700, int((general_occ + icu_occ) * (0.95 + rng.uniform(-0.05, 0.08))))

        synthetic_doc = {
            "region_id": region_id,
            "region_name": region_name,
            "population": population,
            "infrastructure": {
                "general_beds": {"total": general_total, "occupied": general_occ},
                "icu_beds": {"total": icu_total, "occupied": icu_occ},
                "ventilators": {"total": vent_total, "occupied": vent_occ},
                "nurses_on_duty": nurses_on_duty,
            },
            "ppe_inventory": {
                "oxygen_cylinders": oxygen_stock,
                "n95_masks": max(1000, int(population / 1200)),
            },
            "generated": True,
            "generated_reason": "resources_missing_for_region",
            "generated_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
        }

        self.resources_col.update_one(
            {"region_id": region_id},
            {"$set": synthetic_doc},
            upsert=True,
        )

        logger.info(
            "Generated synthetic resources for region=%s disease=%s active_cases=%s",
            region_id,
            disease,
            active_cases,
        )
        return synthetic_doc

    def _get_current_status(self, region_id: str) -> Optional[Dict[str, Any]]:
        """Fetch latest resource snapshot for a canonical region ID."""
        doc = self.resources_col.find_one(
            {"region_id": region_id},
            sort=[("last_updated", DESCENDING)],
        )
        if doc:
            return doc

        return self.resources_col.find_one(
            {"region_id": {"$regex": f"^{re.escape(region_id)}$", "$options": "i"}},
            sort=[("last_updated", DESCENDING)],
        )

    def _get_capacity_snapshot(
        self,
        resource_doc: Dict[str, Any],
        population: int,
    ) -> Dict[str, int]:
        infra = resource_doc.get("infrastructure") or {}
        ppe = resource_doc.get("ppe_inventory") or {}

        general_total, general_occ = self._extract_total_occupied(
            infra.get("general_beds") or infra.get("ward_beds") or infra.get("beds")
        )
        icu_total, icu_occ = self._extract_total_occupied(infra.get("icu_beds") or infra.get("icu"))
        vent_total, vent_occ = self._extract_total_occupied(infra.get("ventilators"))

        regional_general_floor = max(1200, int(population / 2000))
        if general_total <= 0:
            general_total = regional_general_floor
        general_total = max(general_total, regional_general_floor)
        if general_occ <= 0:
            general_occ = int(general_total * 0.72)
        general_occ = min(general_occ, general_total)

        regional_icu_floor = max(140, int(general_total * 0.10))
        if icu_total <= 0:
            icu_total = regional_icu_floor
        icu_total = max(icu_total, regional_icu_floor)
        if icu_occ <= 0:
            icu_occ = int(icu_total * 0.76)
        icu_occ = min(icu_occ, icu_total)

        regional_vent_floor = max(90, int(icu_total * 0.62))
        if vent_total <= 0:
            vent_total = regional_vent_floor
        vent_total = max(vent_total, regional_vent_floor)
        if vent_occ <= 0:
            vent_occ = int(vent_total * 0.72)
        vent_occ = min(vent_occ, vent_total)

        nurses_on_duty = self._extract_count(
            infra.get("nurses_on_duty")
            or infra.get("staff_on_duty")
            or (infra.get("staffing") or {}).get("nurses")
        )
        if nurses_on_duty <= 0:
            nurses_on_duty = max(320, int((general_occ + icu_occ) * 0.55))

        oxygen_stock = self._extract_count(
            ppe.get("oxygen_cylinders")
            or ppe.get("oxygen")
            or (infra.get("oxygen") or {}).get("stock")
        )
        if oxygen_stock <= 0:
            oxygen_stock = max(700, int((general_occ + icu_occ) * 0.9))

        return {
            "general_total": max(general_total, general_occ),
            "general_occ": general_occ,
            "icu_total": max(icu_total, icu_occ),
            "icu_occ": icu_occ,
            "vent_total": vent_total,
            "vent_occ": vent_occ,
            "nurses_on_duty": nurses_on_duty,
            "oxygen_stock": oxygen_stock,
        }

    def predict_demand(
        self,
        region_id: str,
        target_date: str,
        disease: str,
    ) -> ResourcePredictionResponse:
        """Calculate resource demand from cases and current regional capacity."""
        region_meta = self._resolve_region(region_id)
        canonical_region_id = str(region_meta["region_id"]).upper()

        config = self.get_config(disease.lower())
        params = config.resource_params

        region_population = max(100_000, int(region_meta.get("population") or 1_000_000))

        active_cases = self._estimate_active_cases(
            canonical_region_id,
            target_date,
            disease,
            params.avg_stay_days,
        )

        effective_active_cases = max(active_cases, self._baseline_active_cases(region_population, disease))

        pred_general_beds = max(
            math.ceil(effective_active_cases * params.hospitalization_rate),
            max(250, int(region_population / 50000)),
        )
        pred_icu_beds = max(
            math.ceil(effective_active_cases * params.icu_rate),
            max(35, int(pred_general_beds * 0.12)),
        )
        pred_ventilators = max(
            math.ceil(pred_icu_beds * 0.65),
            max(25, int(region_population / 300000)),
        )
        total_pred_hospitalized = pred_general_beds + pred_icu_beds
        pred_nurses = max(
            math.ceil(total_pred_hospitalized * params.nurse_ratio),
            max(180, int(region_population / 250000)),
        )
        pred_oxygen = max(
            math.ceil(total_pred_hospitalized * (params.oxygen_rate or 0.1)),
            max(120, int(region_population / 300000)),
        )

        current_status = self._get_current_status(canonical_region_id)
        if not current_status:
            current_status = self._build_synthetic_resource_doc(
                region_meta=region_meta,
                disease=disease,
                target_date=target_date,
                active_cases=effective_active_cases,
            )

        snapshot = self._get_capacity_snapshot(
            current_status,
            region_population,
        )

        general_util = self._safe_ratio(snapshot["general_occ"] + pred_general_beds, snapshot["general_total"])
        icu_util = self._safe_ratio(snapshot["icu_occ"] + pred_icu_beds, snapshot["icu_total"])
        vent_util = self._safe_ratio(snapshot["vent_occ"] + pred_ventilators, snapshot["vent_total"])
        nurse_util = self._safe_ratio(pred_nurses, snapshot["nurses_on_duty"])
        oxygen_util = self._safe_ratio(pred_oxygen, snapshot["oxygen_stock"])
        urgency_score = max(general_util, icu_util, vent_util, nurse_util, oxygen_util)

        shortage_risk = (
            general_util >= 0.9
            or icu_util >= 0.9
            or vent_util >= 0.9
            or nurse_util >= 0.9
            or oxygen_util >= 0.9
        )
        shortage_level = self._classify_level(urgency_score)

        return ResourcePredictionResponse(
            region_id=canonical_region_id,
            date=target_date,
            disease=disease.upper(),
            forecasted_cases=effective_active_cases,
            resources=ResourceDemand(
                general_beds=pred_general_beds,
                general_beds_capacity=snapshot["general_total"],
                general_beds_occupied=snapshot["general_occ"],
                icu_beds=pred_icu_beds,
                icu_beds_capacity=snapshot["icu_total"],
                icu_beds_occupied=snapshot["icu_occ"],
                ventilators=pred_ventilators,
                ventilators_capacity=snapshot["vent_total"],
                ventilators_occupied=snapshot["vent_occ"],
                nurses=pred_nurses,
                nurses_on_duty=snapshot["nurses_on_duty"],
                oxygen_cylinders=pred_oxygen,
                oxygen_cylinders_stock=snapshot["oxygen_stock"],
            ),
            shortage_risk=shortage_risk,
            shortage_level=shortage_level,
            urgency_score=round(urgency_score, 4),
        )
