"""Generic disease data loader supporting multiple diseases."""
import logging
from pathlib import Path
from typing import List, Dict, Optional
import csv
from datetime import datetime

from backend.services.ingestion import upsert_cases, upsert_regions
from backend.disease_config import get_disease_registry

logger = logging.getLogger(__name__)


class DiseaseDataLoader:
    """Generic loader for disease surveillance data."""
    
    def __init__(self, disease_id: str):
        """Initialize loader for specific disease."""
        self.disease_id = disease_id.upper()
        registry = get_disease_registry()
        self.disease_profile = registry.get_disease(self.disease_id)
        
        if not self.disease_profile:
            raise ValueError(f"Disease '{self.disease_id}' not found in registry")
        
        logger.info(f"Initialized loader for {self.disease_profile.name}")
    
    def load_from_csv(
        self,
        csv_path: Path,
        region_col: str = "State/UT",
        date_col: Optional[str] = None,
        year_col: Optional[str] = None,
        confirmed_col: str = "Cases",
        deaths_col: str = "Deaths",
        recovered_col: Optional[str] = None,
        date_format: str = "%Y-%m-%d"
    ) -> Dict[str, int]:
        """
        Load disease data from CSV file.
        
        Args:
            csv_path: Path to CSV file
            region_col: Column name for region/state
            date_col: Column name for date (if single date column)
            year_col: Column name for year (if date needs to be constructed)
            confirmed_col: Column name for confirmed cases
            deaths_col: Column name for deaths
            recovered_col: Column name for recovered (optional)
            date_format: Date format string
        
        Returns:
            Dictionary with counts of loaded regions and cases
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        regions = []
        cases = []
        region_ids_seen = set()
        
        logger.info(f"Loading {self.disease_id} data from {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Extract region
                region_name = row.get(region_col, "").strip()
                if not region_name:
                    continue
                
                # Create region_id (normalized)
                region_id = region_name.upper().replace(" ", "_").replace("&", "AND")
                
                # Add region if not seen
                if region_id not in region_ids_seen:
                    regions.append({
                        "region_id": region_id,
                        "name": region_name,
                        "country": "India",  # Default - can be parameterized
                        "disease": self.disease_id
                    })
                    region_ids_seen.add(region_id)
                
                # Extract date
                if date_col:
                    date_str = row.get(date_col, "").strip()
                    try:
                        date_obj = datetime.strptime(date_str, date_format)
                        date_iso = date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        logger.warning(f"Invalid date format: {date_str}")
                        continue
                elif year_col:
                    year = row.get(year_col, "").strip()
                    if not year:
                        continue
                    # Use Jan 1 of that year as default
                    date_iso = f"{year}-01-01"
                else:
                    logger.error("Must provide either date_col or year_col")
                    raise ValueError("Date column specification required")
                
                # Extract case counts
                try:
                    confirmed = int(row.get(confirmed_col, 0))
                    deaths = int(row.get(deaths_col, 0))
                    recovered = int(row.get(recovered_col, 0)) if recovered_col and row.get(recovered_col) else 0
                except ValueError as e:
                    logger.warning(f"Invalid numeric value in row: {e}")
                    continue
                
                cases.append({
                    "region_id": region_id,
                    "date": date_iso,
                    "confirmed": confirmed,
                    "deaths": deaths,
                    "recovered": recovered,
                    "disease": self.disease_id
                })
        
        # Upsert to database
        regions_inserted = upsert_regions(regions)
        cases_inserted = upsert_cases(cases)
        
        logger.info(
            f"✅ Loaded {self.disease_id} data: "
            f"{regions_inserted} new regions, {cases_inserted} new case records"
        )
        
        return {
            "regions_loaded": len(regions),
            "regions_new": regions_inserted,
            "cases_loaded": len(cases),
            "cases_new": cases_inserted,
            "disease": self.disease_id
        }
    
    def load_from_dict(
        self,
        data: List[Dict],
        region_id_field: str = "region_id",
        date_field: str = "date",
        confirmed_field: str = "confirmed",
        deaths_field: str = "deaths",
        recovered_field: str = "recovered"
    ) -> Dict[str, int]:
        """
        Load disease data from list of dictionaries.
        
        Useful for loading from APIs or JSON files.
        """
        cases = []
        
        for record in data:
            cases.append({
                "region_id": record.get(region_id_field),
                "date": record.get(date_field),
                "confirmed": record.get(confirmed_field, 0),
                "deaths": record.get(deaths_field, 0),
                "recovered": record.get(recovered_field, 0),
                "disease": self.disease_id
            })
        
        cases_inserted = upsert_cases(cases)
        
        logger.info(f"✅ Loaded {cases_inserted} new {self.disease_id} case records from dictionary data")
        
        return {
            "cases_loaded": len(cases),
            "cases_new": cases_inserted,
            "disease": self.disease_id
        }


def load_dengue_data(csv_path: Path) -> Dict[str, int]:
    """Load dengue data (backward compatibility)."""
    loader = DiseaseDataLoader("DENGUE")
    return loader.load_from_csv(
        csv_path=csv_path,
        region_col="State/UT",
        year_col="Year",
        confirmed_col="Cases",
        deaths_col="Deaths"
    )


def load_covid_data(csv_path: Path) -> Dict[str, int]:
    """Load COVID-19 data from CSV."""
    loader = DiseaseDataLoader("COVID")
    return loader.load_from_csv(
        csv_path=csv_path,
        region_col="State/UT",
        date_col="Date",
        confirmed_col="Confirmed",
        deaths_col="Deaths",
        recovered_col="Recovered",
        date_format="%Y-%m-%d"
    )


def load_malaria_data(csv_path: Path) -> Dict[str, int]:
    """Load Malaria data from CSV."""
    loader = DiseaseDataLoader("MALARIA")
    return loader.load_from_csv(
        csv_path=csv_path,
        region_col="State/UT",
        year_col="Year",
        confirmed_col="Cases",
        deaths_col="Deaths"
    )


def load_generic_disease_data(
    disease_id: str,
    csv_path: Path,
    **kwargs
) -> Dict[str, int]:
    """
    Load data for any disease in the registry.
    
    Args:
        disease_id: Disease identifier (e.g., "TUBERCULOSIS", "INFLUENZA")
        csv_path: Path to CSV file
        **kwargs: Additional arguments to pass to load_from_csv
    
    Returns:
        Dictionary with load statistics
    """
    loader = DiseaseDataLoader(disease_id)
    return loader.load_from_csv(csv_path=csv_path, **kwargs)
