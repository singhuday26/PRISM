import logging
from typing import List, Dict, Optional
from ..db import get_db

logger = logging.getLogger(__name__)


def compute_hotspots(limit: int = 5, disease: Optional[str] = None) -> List[Dict]:
    """Compute top hotspots by confirmed cases using aggregation, optionally filtered by disease."""
    try:
        db = get_db()
        
        # Add match stage if disease filter is specified
        pipeline = []
        if disease:
            pipeline.append({"$match": {"disease": disease}})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": "$region_id",
                    "confirmed_sum": {"$sum": "$confirmed"},
                    "deaths_sum": {"$sum": "$deaths"},
                    "latest_date": {"$max": "$date"},
                }
            },
            {"$addFields": {"region_id": "$_id"}},
            {
                "$lookup": {
                    "from": "regions",
                    "localField": "region_id",
                    "foreignField": "region_id",
                    "as": "region",
                }
            },
            {"$unwind": {"path": "$region", "preserveNullAndEmptyArrays": True}},
            {"$addFields": {"region_name": "$region.region_name"}},
            {
                "$project": {
                    "_id": 0,
                    "region_id": 1,
                    "region_name": 1,
                    "confirmed_sum": 1,
                    "deaths_sum": 1,
                    "latest_date": 1,
                }
            },
            {"$sort": {"confirmed_sum": -1}},
            {"$limit": limit},
        ])
        
        results = list(db["cases_daily"].aggregate(pipeline))
        disease_info = f" for disease: {disease}" if disease else ""
        logger.info(f"Computed {len(results)} hotspots{disease_info}")
        return results
    except Exception as e:
        logger.error(f"Error computing hotspots: {e}")
        raise
