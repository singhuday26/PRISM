import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from pymongo.errors import PyMongoError
from ..db import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


def _list_regions_impl(disease: Optional[str] = Query(None, description="Filter by disease")):
    """List all regions, optionally filtered by disease."""
    try:
        db = get_db()
        query = {"disease": disease} if disease else {}
        docs = list(db["regions"].find(query, {"_id": 0}))
        
        disease_info = f" for disease: {disease}" if disease else ""
        logger.info(f"Retrieved {len(docs)} regions{disease_info}")
        
        response = {"regions": docs, "count": len(docs)}
        if disease:
            response["disease"] = disease
        return response
    except PyMongoError as e:
        logger.error(f"Database error listing regions: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred while fetching regions",
        )
    except Exception as e:
        logger.error(f"Unexpected error listing regions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get("")
def list_regions_no_slash(disease: Optional[str] = Query(None, description="Filter by disease")):
    """List all regions without requiring a trailing slash in URL."""
    return _list_regions_impl(disease)


@router.get("/")
def list_regions(disease: Optional[str] = Query(None, description="Filter by disease")):
    """List all regions, optionally filtered by disease."""
    return _list_regions_impl(disease)


@router.get("/diseases")
def list_diseases():
    """List all available diseases with full metadata, derived from case data."""
    try:
        db = get_db()
        # Get distinct disease IDs present in our epidemiological data (cases_daily)
        # instead of the regions collection which doesn't store this field
        disease_ids = db["cases_daily"].distinct("disease")
        disease_ids = [d for d in disease_ids if d is not None]
        
        # Get registry metadata
        from backend.disease_config import get_disease_registry
        registry = get_disease_registry()
        
        disease_list = []
        for d_id in disease_ids:
            profile = registry.get_disease(d_id)
            if profile:
                disease_list.append({
                    "disease_id": profile.disease_id,
                    "name": profile.name,
                    "transmission_mode": profile.transmission_mode,
                    "severity": profile.severity
                })
            else:
                # Fallback for data present in cases but missing in registry
                disease_list.append({
                    "disease_id": d_id,
                    "name": str(d_id).replace("_", " ").title(),
                    "transmission_mode": "unknown",
                    "severity": "medium"
                })
        
        # Sort alphabetically by name
        disease_list.sort(key=lambda x: x["name"])
        
        logger.info(f"Retrieved {len(disease_list)} diseases from case data")
        return {"diseases": disease_list, "count": len(disease_list)}
    except PyMongoError as e:
        logger.error(f"Database error listing diseases: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred while fetching diseases",
        )
    except Exception as e:
        logger.error(f"Unexpected error listing diseases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

