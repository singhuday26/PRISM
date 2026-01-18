from datetime import datetime, timedelta
from ..db import ensure_indexes
from ..services.ingestion import upsert_regions, upsert_cases


def run() -> None:
    ensure_indexes()

    regions = [
        {"region_id": "IN-AP", "region_name": "Andhra Pradesh"},
        {"region_id": "IN-TN", "region_name": "Tamil Nadu"},
    ]

    start_date = datetime(2021, 5, 1)
    cases = []
    for i in range(10):
        date_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        cases.append({
            "region_id": "IN-AP",
            "date": date_str,
            "confirmed": 1000 + i * 120,
            "deaths": 10 + i,
            "recovered": 400 + i * 90,
        })
        cases.append({
            "region_id": "IN-TN",
            "date": date_str,
            "confirmed": 1500 + i * 80,
            "deaths": 15 + i,
            "recovered": 600 + i * 70,
        })

    new_regions = upsert_regions(regions)
    new_cases = upsert_cases(cases)
    print(f"Inserted {new_regions} new regions, {new_cases} new case rows.")


if __name__ == "__main__":
    run()
