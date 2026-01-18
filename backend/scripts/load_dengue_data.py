"""
Dengue data loader for PRISM.
Loads Dengue_STATEWISE_DEATH_3yrs.csv from data.gov.in into MongoDB.
"""
import argparse
import logging
import re
import pandas as pd
from typing import Dict, List, Tuple
from ..db import ensure_indexes, get_db
from ..services.ingestion import upsert_regions, upsert_cases

logger = logging.getLogger(__name__)


def create_region_id(state_name: str, existing_ids: set) -> str:
    """
    Create region_id in format IN-XX where XX is first 2 letters of state uppercase.
    Ensures uniqueness by appending numbers if duplicate.
    
    Args:
        state_name: Name of the state/UT
        existing_ids: Set of already used region IDs
        
    Returns:
        Unique region_id in format IN-XX or IN-XX2, IN-XX3, etc.
    """
    # Remove special characters and get first 2 letters
    clean_name = re.sub(r'[^a-zA-Z\s]', '', state_name).strip()
    words = clean_name.split()
    
    if not words:
        # Fallback if no valid characters
        prefix = "XX"
    elif len(words) == 1:
        # Single word: take first 2 letters
        prefix = words[0][:2].upper()
    else:
        # Multiple words: take first letter of first two words
        prefix = (words[0][0] + words[1][0]).upper()
    
    base_id = f"IN-{prefix}"
    
    # Ensure uniqueness
    region_id = base_id
    counter = 2
    while region_id in existing_ids:
        region_id = f"{base_id}{counter}"
        counter += 1
    
    existing_ids.add(region_id)
    return region_id


def parse_dengue_csv(csv_path: str) -> Tuple[List[Dict], List[Dict], Dict]:
    """
    Parse dengue CSV and transform to PRISM format.
    
    Returns:
        Tuple of (regions, cases, stats)
    """
    df = pd.read_csv(csv_path)
    
    # Detect year columns
    year_pattern = re.compile(r'(\d{4})')
    case_columns = {}
    death_columns = {}
    
    for col in df.columns:
        year_match = year_pattern.search(col)
        if year_match:
            year = year_match.group(1)
            if 'case' in col.lower():
                case_columns[year] = col
            elif 'death' in col.lower():
                death_columns[year] = col
    
    years = sorted(set(case_columns.keys()) | set(death_columns.keys()))
    
    if not years:
        raise ValueError("No year columns found in CSV")
    
    logger.info(f"Detected years: {years}")
    logger.info(f"Case columns: {case_columns}")
    logger.info(f"Death columns: {death_columns}")
    
    # Process data
    regions = []
    cases = []
    existing_ids = set()
    state_col = 'State/UT'
    
    total_rows = 0
    for idx, row in df.iterrows():
        state_name = str(row[state_col]).strip()
        
        # Skip invalid rows
        if not state_name or state_name.lower() in ['nan', 'total', 'all']:
            continue
        
        total_rows += 1
        region_id = create_region_id(state_name, existing_ids)
        
        # Create region record
        regions.append({
            "region_id": region_id,
            "region_name": state_name,
            "country": "India",
            "source": "data.gov.in",
            "disease": "DENGUE"
        })
        
        # Create case records for each year
        for year in years:
            confirmed = 0
            deaths = 0
            
            if year in case_columns:
                try:
                    confirmed = int(row[case_columns[year]])
                except (ValueError, TypeError):
                    confirmed = 0
            
            if year in death_columns:
                try:
                    deaths = int(row[death_columns[year]])
                except (ValueError, TypeError):
                    deaths = 0
            
            # Create case record
            cases.append({
                "region_id": region_id,
                "date": f"{year}-01-01",
                "confirmed": confirmed,
                "deaths": deaths,
                "recovered": 0,
                "disease": "DENGUE"
            })
    
    stats = {
        "total_rows": total_rows,
        "total_regions": len(regions),
        "total_cases": len(cases),
        "min_year": min(years),
        "max_year": max(years),
        "years": years
    }
    
    return regions, cases, stats


def reset_dengue_data() -> Dict[str, int]:
    """
    Delete all dengue records from database.
    
    Returns:
        Dictionary with counts of deleted records
    """
    db = get_db()
    
    # Delete dengue cases
    cases_result = db["cases_daily"].delete_many({"disease": "DENGUE"})
    
    # Delete dengue regions
    regions_result = db["regions"].delete_many({"source": "data.gov.in", "disease": "DENGUE"})
    
    return {
        "cases_deleted": cases_result.deleted_count,
        "regions_deleted": regions_result.deleted_count
    }


def upsert_dengue_regions(regions: List[Dict]) -> int:
    """Upsert dengue regions into database."""
    db = get_db()
    inserted = 0
    for region in regions:
        res = db["regions"].update_one(
            {"region_id": region["region_id"]},
            {"$set": region},
            upsert=True,
        )
        if res.upserted_id or res.modified_count > 0:
            inserted += 1
    return inserted


def upsert_dengue_cases(cases: List[Dict]) -> int:
    """Upsert dengue cases into database using unique key (region_id, date, disease)."""
    db = get_db()
    inserted = 0
    for case in cases:
        res = db["cases_daily"].update_one(
            {
                "region_id": case["region_id"],
                "date": case["date"],
                "disease": case.get("disease", "DENGUE")
            },
            {"$set": case},
            upsert=True,
        )
        if res.upserted_id or res.modified_count > 0:
            inserted += 1
    return inserted


def run(csv_path: str = "Datasets/Dengue_STATEWISE_DEATH_3yrs.csv", reset: bool = False) -> None:
    """
    Load dengue data into MongoDB.
    
    Args:
        csv_path: Path to dengue CSV file
        reset: If True, delete existing dengue data before loading
    """
    logging.basicConfig(level=logging.INFO)
    
    ensure_indexes()
    
    # Reset if requested
    if reset:
        logger.info("🗑️  Resetting dengue data...")
        deleted = reset_dengue_data()
        print(f"✓ Deleted {deleted['cases_deleted']} case records")
        print(f"✓ Deleted {deleted['regions_deleted']} region records")
    
    # Parse CSV
    logger.info(f"📖 Loading data from {csv_path}")
    regions, cases, stats = parse_dengue_csv(csv_path)
    
    print("\n📊 Summary:")
    print(f"   Total rows read: {stats['total_rows']}")
    print(f"   Total regions: {stats['total_regions']}")
    print(f"   Total case records: {stats['total_cases']}")
    print(f"   Years loaded: {stats['min_year']} - {stats['max_year']}")
    print(f"   Year breakdown: {', '.join(stats['years'])}")
    
    # Upsert into database
    logger.info("💾 Upserting regions...")
    regions_upserted = upsert_dengue_regions(regions)
    logger.info(f"✓ Upserted {regions_upserted} regions")
    
    logger.info("💾 Upserting case records...")
    cases_upserted = upsert_dengue_cases(cases)
    logger.info(f"✓ Upserted {cases_upserted} case records")
    
    print("\n✅ Dengue data loaded successfully!")
    print(f"   Regions upserted: {regions_upserted}")
    print(f"   Case records upserted: {cases_upserted}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load dengue data into PRISM")
    parser.add_argument(
        "--csv",
        default="Datasets/Dengue_STATEWISE_DEATH_3yrs.csv",
        help="Path to dengue CSV file"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing dengue data before loading"
    )
    
    args = parser.parse_args()
    run(csv_path=args.csv, reset=args.reset)
