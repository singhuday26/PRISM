"""
CSV loader for Kaggle COVID-19 dataset.
Transforms the Kaggle format into PRISM's expected schema and loads into MongoDB.
"""
import pandas as pd
from datetime import datetime
from ..services.ingestion import upsert_cases, upsert_regions
from ..db import ensure_indexes


def parse_date(date_str: str) -> str:
    """Convert various date formats to YYYY-MM-DD."""
    for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"]:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str


def transform_kaggle_format(csv_path: str, country_filter: str = "India") -> tuple:
    """
    Transform Kaggle COVID-19 dataset to PRISM format.
    
    Expected input columns: SNo,ObservationDate,Province/State,Country/Region,Last Update,Confirmed,Deaths,Recovered
    Output: region_id, date, confirmed, deaths, recovered
    """
    df = pd.read_csv(csv_path)
    
    # Filter by country if specified
    if country_filter:
        df = df[df["Country/Region"] == country_filter]
    
    if df.empty:
        print(f"No data found for country: {country_filter}")
        return [], []
    
    # Create region_id from Province/State or Country/Region
    df["region_id"] = df.apply(
        lambda row: f"{row['Country/Region']}-{row['Province/State']}" 
        if pd.notna(row['Province/State']) and row['Province/State'].strip() != ""
        else row['Country/Region'],
        axis=1
    )
    
    # Parse and standardize date
    df["date"] = df["ObservationDate"].apply(parse_date)
    
    # Fill NaN values with 0
    df["Confirmed"] = df["Confirmed"].fillna(0).astype(int)
    df["Deaths"] = df["Deaths"].fillna(0).astype(int)
    df["Recovered"] = df["Recovered"].fillna(0).astype(int)
    
    # Rename columns to match PRISM schema
    df_clean = df[["region_id", "date", "Confirmed", "Deaths", "Recovered"]].copy()
    df_clean.columns = ["region_id", "date", "confirmed", "deaths", "recovered"]
    
    # Create region records
    unique_regions = df_clean[["region_id"]].drop_duplicates()
    unique_regions["region_name"] = unique_regions["region_id"].str.replace("-", " - ")
    regions = unique_regions.to_dict(orient="records")
    
    # Create case records
    cases = df_clean.to_dict(orient="records")
    
    return regions, cases


def run(csv_path: str, country: str = "India", limit: int = None) -> None:
    """Load Kaggle COVID-19 data into MongoDB."""
    from ..db import get_db
    from pymongo import UpdateOne
    
    ensure_indexes()
    
    print(f"Loading data from {csv_path} for country: {country}")
    regions, cases = transform_kaggle_format(csv_path, country)
    
    if not regions or not cases:
        print("No data to load.")
        return
    
    # Apply limit if specified (for testing)
    if limit:
        cases = cases[:limit]
        print(f"⚠️  Limited to first {limit} records for testing")
    
    # Batch insert regions
    db = get_db()
    regions_col = db["regions"]
    cases_col = db["cases_daily"]
    
    print(f"Upserting {len(regions)} regions...")
    region_ops = [
        UpdateOne(
            {"region_id": r["region_id"]},
            {"$setOnInsert": r},
            upsert=True
        )
        for r in regions
    ]
    region_result = regions_col.bulk_write(region_ops, ordered=False)
    
    print(f"Upserting {len(cases)} case records (this may take a minute)...")
    # Process in batches of 1000 to avoid memory issues
    batch_size = 1000
    total_inserted = 0
    
    for i in range(0, len(cases), batch_size):
        batch = cases[i:i + batch_size]
        case_ops = [
            UpdateOne(
                {"region_id": c["region_id"], "date": c["date"]},
                {"$setOnInsert": c},
                upsert=True
            )
            for c in batch
        ]
        result = cases_col.bulk_write(case_ops, ordered=False)
        total_inserted += result.upserted_count
        if (i + batch_size) % 5000 == 0:
            print(f"  Processed {i + batch_size}/{len(cases)} records...")
    
    print(f"✅ Loaded {region_result.upserted_count} new regions")
    print(f"✅ Loaded {total_inserted} new case records")
    print(f"📊 Total regions: {len(regions)}, Total cases: {len(cases)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load Kaggle COVID-19 data into PRISM")
    parser.add_argument("csv_path", type=str, help="Path to covid_19_data.csv")
    parser.add_argument("--country", type=str, default="India", help="Country to filter (default: India)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of records (for testing)")
    args = parser.parse_args()
    
    run(args.csv_path, args.country, args.limit)
