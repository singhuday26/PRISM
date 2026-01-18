import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from pymongo.errors import PyMongoError
from ..db import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
def list_regions(disease: Optional[str] = Query(None, description="Filter by disease")):
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


@router.get("/diseases")
def list_diseases():
    """List all available diseases in the database."""
    try:
        db = get_db()
        # Get distinct diseases from regions collection
        diseases = db["regions"].distinct("disease")
        # Filter out None values
        diseases = [d for d in diseases if d is not None]
        diseases.sort()
        
        logger.info(f"Retrieved {len(diseases)} diseases")
        return {"diseases": diseases, "count": len(diseases)}
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

