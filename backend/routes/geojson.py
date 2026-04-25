"""
GeoJSON API routes for risk heatmap visualization.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.services.geojson import get_risk_geojson, get_region_boundaries
from backend.services.derived_data_bootstrap import ensure_derived_data_for_disease

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/geojson")
def get_risk_as_geojson(
    date: Optional[str] = Query(None, description="Date for risk scores (YYYY-MM-DD)"),
    disease: Optional[str] = Query(None, description="Filter by disease type")
):
    """
    Get risk scores formatted as GeoJSON for map rendering.
    
    Args:
        date: Optional date filter (defaults to latest)
        disease: Optional disease filter
        
    Returns:
        GeoJSON FeatureCollection with risk data
    """
    try:
        normalized_disease = disease.strip().upper() if disease else None
        geojson = get_risk_geojson(target_date=date, disease=normalized_disease)

        if normalized_disease and not geojson.get("features"):
            ensure_derived_data_for_disease(normalized_disease)
            geojson = get_risk_geojson(target_date=date, disease=normalized_disease)

        return JSONResponse(
            content=geojson,
            headers={"Content-Type": "application/geo+json"}
        )
    except Exception as e:
        logger.error(f"Error getting risk GeoJSON: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@router.get("/boundaries")
def get_boundaries():
    """
    Get region boundary polygons for map rendering.
    
    Returns:
        GeoJSON FeatureCollection with region boundaries
    """
    try:
        boundaries = get_region_boundaries()
        return JSONResponse(
            content=boundaries,
            headers={"Content-Type": "application/geo+json"}
        )
    except Exception as e:
        logger.error(f"Error getting boundaries: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
