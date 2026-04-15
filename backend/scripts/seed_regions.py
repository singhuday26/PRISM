"""Seed minimal region data for local dashboard validation."""

from backend.db import ensure_indexes, get_db


REGIONS = [
    {
        "region_id": "IN-MH",
        "region_name": "Maharashtra",
        "population": 112374333,
        "lat": 19.7515,
        "lon": 75.7139,
    },
    {
        "region_id": "IN-DL",
        "region_name": "Delhi",
        "population": 16787941,
        "lat": 28.7041,
        "lon": 77.1025,
    },
]


def run() -> None:
    ensure_indexes()
    db = get_db()
    regions_col = db["regions"]

    inserted_or_updated = 0
    for region in REGIONS:
        result = regions_col.update_one(
            {"region_id": region["region_id"]},
            {"$set": region},
            upsert=True,
        )
        if result.upserted_id is not None or result.modified_count > 0:
            inserted_or_updated += 1

    total_regions = regions_col.count_documents({})
    print(f"Seed complete. Inserted/updated: {inserted_or_updated}, total regions: {total_regions}")


if __name__ == "__main__":
    run()
