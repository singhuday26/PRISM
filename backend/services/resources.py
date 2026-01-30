
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta, date

from pymongo import DESCENDING

from backend.db import get_db
from backend.schemas.responses import (
    ResourceConfig, 
    ResourceConfigParams, 
    ResourceDemand, 
    ResourcePredictionResponse
)
from backend.exceptions import DataNotFoundError

logger = logging.getLogger(__name__)

class ResourceService:
    def __init__(self):
        self.db = get_db()
        self.config_col = self.db["disease_config"]
        self.forecasts_col = self.db["forecasts_daily"]

    def get_config(self, disease: str) -> ResourceConfig:
        """Get resource configuration for a disease."""
        doc = self.config_col.find_one({"_id": disease})
        if not doc:
            # Return sensible defaults if not found
            logger.warning(f"No resource config found for {disease}, using defaults")
            return ResourceConfig(
                disease=disease,
                resource_params=ResourceConfigParams(
                    hospitalization_rate=0.1,
                    icu_rate=0.01,
                    avg_stay_days=7,
                    nurse_ratio=0.1,
                    oxygen_rate=0.1
                )
            )
        
        return ResourceConfig(
            disease=doc["name"], # stored as name in seed, _id is slug
            resource_params=ResourceConfigParams(**doc["resource_params"])
        )

    def set_config(self, config: ResourceConfig) -> None:
        """Update resource configuration."""
        self.config_col.update_one(
            {"_id": config.disease.lower()}, # usage slug as ID
            {
                "$set": {
                    "name": config.disease,
                    "resource_params": config.resource_params.model_dump()
                }
            },
            upsert=True
        )

    def _estimate_active_cases(
        self, 
        region_id: str, 
        target_date: str, 
        disease: str, 
        avg_stay_days: int
    ) -> int:
        """
        Estimate active cases by summing new cases over the last N days (avg_stay_days).
        Integrates both historical data (cases_daily) and future forecasts (forecasts_daily).
        """
        target_dt = date.fromisoformat(target_date)
        start_dt = target_dt - timedelta(days=avg_stay_days - 1)
        start_date = start_dt.isoformat()

        # Query 1: Historical Data (cases_daily)
        # Uses 'confirmed' field
        hist_cursor = self.db["cases_daily"].find({
            "region_id": region_id,
            "disease": disease,
            "date": {"$gte": start_date, "$lte": target_date}
        })
        
        # Query 2: Forecast Data (forecasts_daily)
        # Uses 'cases' or 'pred_mean' field
        forecast_cursor = self.forecasts_col.find({
            "region_id": region_id,
            "disease": disease,
            "date": {"$gte": start_date, "$lte": target_date}
        })
        
        # Merge data by date to avoid double counting if overlaps exist
        daily_counts = {}
        
        # Prefer historical data
        hist_count = 0
        for doc in hist_cursor:
            d = doc["date"]
            count = doc.get("confirmed", 0)
            daily_counts[d] = count
            hist_count += 1
            
        # Fill gaps with forecast data
        fc_count = 0
        for doc in forecast_cursor:
            d = doc["date"]
            if d not in daily_counts:
                # Handle inconsistent field names
                count = doc.get("cases") or doc.get("pred_mean") or 0
                daily_counts[d] = count
            fc_count += 1
        
        total_active = sum(daily_counts.values())
        
        if total_active == 0 and avg_stay_days > 0:
            logger.warning(f"No case data found for {region_id} {disease} window {start_date} to {target_date}")
            
        return int(total_active)

    def predict_demand(
        self, 
        region_id: str, 
        target_date: str, 
        disease: str
    ) -> ResourcePredictionResponse:
        """
        Calculate resource demand based on forecasted cases and disease config.
        """
        # 1. Get Config
        config = self.get_config(disease)
        params = config.resource_params
        
        # 2. Estimate Active Cases
        active_cases = self._estimate_active_cases(
            region_id, 
            target_date, 
            disease, 
            params.avg_stay_days
        )
        
        # 3. Apply Multipliers
        general_beds = int(active_cases * params.hospitalization_rate)
        icu_beds = int(active_cases * params.icu_rate)
        # Nurse ratio is per patient (hospitalized), usually. Spec says generic nurse ratio.
        # Let's assume nurse_ratio is per hospitalized patient.
        # Spec says: "1 nurse per 10 patients" -> ratio 0.1
        # Applied to total hospitalized (General + ICU)? Or just General?
        # Usually ICU needs 1:1 or 1:2. General 1:10.
        # For MVP, applying simpler logic: Total Hospitalized * nurse_ratio
        total_hospitalized = general_beds + icu_beds
        nurses = int(total_hospitalized * params.nurse_ratio)
        
        oxygen_cylinders = int(total_hospitalized * params.oxygen_rate)

        # 4. Construct Response
        return ResourcePredictionResponse(
            region_id=region_id,
            date=target_date,
            disease=disease,
            forecasted_cases=active_cases,
            resources=ResourceDemand(
                general_beds=general_beds,
                icu_beds=icu_beds,
                nurses=nurses,
                oxygen_cylinders=oxygen_cylinders
            ),
            shortage_risk=False # Placeholder: would need capacity data to determine
        )
