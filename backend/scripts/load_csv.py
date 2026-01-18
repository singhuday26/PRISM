import pandas as pd
from ..services.ingestion import upsert_cases
from ..db import ensure_indexes


REQUIRED_COLUMNS = {"region_id", "date", "confirmed", "deaths", "recovered"}


def run(csv_path: str) -> None:
    ensure_indexes()
    df = pd.read_csv(csv_path)
    if not REQUIRED_COLUMNS.issubset(set(df.columns)):
        missing = REQUIRED_COLUMNS - set(df.columns)
        raise ValueError(f"Missing columns: {missing}")

    records = df.to_dict(orient="records")
    inserted = upsert_cases(records)
    print(f"Inserted {inserted} new case rows from {csv_path}.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load cases CSV into MongoDB")
    parser.add_argument("csv_path", type=str, help="Path to CSV file")
    args = parser.parse_args()
    run(args.csv_path)
