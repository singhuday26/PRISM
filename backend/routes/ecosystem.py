"""API routes for the Ecosystem Wing."""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from backend.services.ecosystem import (
    compute_ecosystem_summary,
    get_institution_detail,
    get_institutions,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/institutions")
def list_institutions(
    type: Optional[str] = Query(None, description="Filter by institution type"),
    region_id: Optional[str] = Query(None, description="Filter by region ID"),
    status: Optional[str] = Query(None, description="Filter by operational status"),
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(100, ge=1, le=500),
):
    """List all connected institutions with optional filters."""
    try:
        docs = get_institutions(
            inst_type=type,
            region_id=region_id,
            status=status,
            search=search,
            limit=limit,
        )
        return {"institutions": docs, "count": len(docs)}
    except Exception as e:
        logger.error("Error listing institutions: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if isinstance(status, type) else 500,
            detail="Failed to list institutions",
        )


@router.get("/institutions/{institution_id}")
def get_institution(institution_id: str):
    """Get detailed information for a single institution."""
    doc = get_institution_detail(institution_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Institution not found")
    return doc


@router.get("/summary")
def ecosystem_summary():
    """Get aggregate ecosystem health summary with cross-institution alerts."""
    try:
        return compute_ecosystem_summary()
    except Exception as e:
        logger.error("Error computing ecosystem summary: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to compute ecosystem summary")
