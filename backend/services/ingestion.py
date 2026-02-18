import logging
from typing import Iterable, Dict
from pymongo.errors import PyMongoError
from ..db import get_db

logger = logging.getLogger(__name__)


def upsert_regions(regions: Iterable[Dict]) -> int:
    """Upsert region documents with disease isolation."""
    try:
        db = get_db()
        inserted = 0
        for region in regions:
            # Build query filter including disease for proper isolation
            query_filter = {"region_id": region["region_id"]}
            # Include disease if present (for disease-specific region metadata)
            if "disease" in region and region["disease"] is not None:
                query_filter["disease"] = region["disease"]

            res = db["regions"].update_one(
                query_filter,
                {"$set": region},
                upsert=True,
            )
            if res.upserted_id:
                inserted += 1
        logger.info(f"Upserted {inserted} new regions")
        return inserted
    except PyMongoError as e:
        logger.error(f"Database error upserting regions: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error upserting regions: {e}")
        raise


def upsert_cases(cases: Iterable[Dict]) -> int:
    """Upsert case documents with disease isolation."""
    try:
        db = get_db()
        inserted = 0
        for case in cases:
            # Build query filter including disease for proper isolation
            query_filter = {
                "region_id": case["region_id"],
                "date": case["date"],
            }
            # Include disease in filter if present
            if "disease" in case and case["disease"] is not None:
                query_filter["disease"] = case["disease"]

            res = db["cases_daily"].update_one(
                query_filter,
                {"$setOnInsert": case},
                upsert=True,
            )
            if res.upserted_id:
                inserted += 1
        logger.info(f"Upserted {inserted} new case records")
        return inserted
    except PyMongoError as e:
        logger.error(f"Database error upserting cases: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error upserting cases: {e}")
        raise
