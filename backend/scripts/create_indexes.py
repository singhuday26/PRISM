from pymongo import ASCENDING, DESCENDING

from backend.db import get_db


def ensure_indexes() -> None:
    db = get_db()

    index_specs = [
        ("regions", db["regions"].create_index("region_id", unique=True)),
        (
            "cases_daily",
            db["cases_daily"].create_index(
                [("region_id", ASCENDING), ("date", ASCENDING)], unique=True
            ),
        ),
        (
            "cases_daily",
            db["cases_daily"].create_index("date"),
        ),
        (
            "risk_scores",
            db["risk_scores"].create_index(
                [
                    ("region_id", ASCENDING),
                    ("updated_at", DESCENDING),
                ]
            ),
        ),
        (
            "alerts",
            db["alerts"].create_index(
                [
                    ("region_id", ASCENDING),
                    ("created_at", DESCENDING),
                ]
            ),
        ),
        (
            "forecasts_daily",
            db["forecasts_daily"].create_index(
                [
                    ("region_id", ASCENDING),
                    ("date", ASCENDING),
                ]
            ),
        ),
    ]

    for collection, index_name in index_specs:
        print(f"Created/verified index '{index_name}' on collection '{collection}'")

    print("All indexes ensured.")


def main() -> None:
    ensure_indexes()


if __name__ == "__main__":
    main()
