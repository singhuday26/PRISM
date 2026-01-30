"""
GeoJSON service for transforming risk data into map-compatible format.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import date

from backend.db import get_db

logger = logging.getLogger(__name__)

# India state boundaries (simplified GeoJSON coordinates)
# These are approximate centroids/simplified polygons for visualization
# India state boundaries (simplified GeoJSON coordinates)
# Contains Polygons for key demo regions, Points for others
INDIA_STATE_GEOMETRIES = {
    "IN-MH": {
        "name": "Maharashtra", 
        "type": "Polygon",
        "center": [75.7139, 19.7515],
        "coordinates": [[
            [72.6, 20.0], [74.5, 22.0], [78.0, 21.5], [80.5, 20.0], 
            [80.0, 18.5], [77.0, 17.5], [74.0, 16.0], [73.0, 16.5], 
            [72.6, 20.0]
        ]]
    },
    "IN-KA": {
        "name": "Karnataka", 
        "type": "Polygon",
        "center": [75.71, 15.32],
        "coordinates": [[
            [74.0, 15.0], [77.5, 18.0], [77.5, 14.0], [78.0, 13.0], 
            [76.0, 11.5], [75.0, 12.0], [74.0, 15.0]
        ]]
    },
    "IN-TN": {
        "name": "Tamil Nadu", 
        "type": "Polygon",
        "center": [78.66, 11.13],
        "coordinates": [[
            [76.0, 11.5], [78.0, 13.5], [80.3, 13.5], [79.8, 10.0], 
            [77.5, 8.0], [76.0, 11.5]
        ]]
    },
    "IN-DL": {
        "name": "Delhi", 
        "type": "Polygon",
        "center": [77.1, 28.7],
        "coordinates": [[
            [76.8, 28.4], [77.3, 28.4], [77.3, 28.9], [76.8, 28.9], [76.8, 28.4]
        ]]
    },
    "IN-WB": {
        "name": "West Bengal", 
        "type": "Polygon",
        "center": [87.85, 23.81],
        "coordinates": [[
            [86.0, 22.0], [88.0, 27.0], [89.8, 26.5], [89.0, 21.5], [86.0, 22.0]
        ]]
    },
    # Fallback Points for others
    "IN-AP": {"name": "Andhra Pradesh", "center": [79.74, 15.91], "type": "Point"},
    "IN-GJ": {"name": "Gujarat", "center": [71.19, 22.26], "type": "Point"},
    "IN-KL": {"name": "Kerala", "center": [76.27, 10.85], "type": "Point"},
    "IN-UP": {"name": "Uttar Pradesh", "center": [80.95, 26.85], "type": "Point"},
}

# Risk level color mapping
RISK_COLORS = {
    "LOW": "#22c55e",      # Green
    "MEDIUM": "#eab308",   # Yellow
    "HIGH": "#f97316",     # Orange
    "CRITICAL": "#ef4444", # Red
}


def get_risk_level(score: float) -> str:
    """Convert risk score to risk level."""
    if score >= 0.7:
        return "CRITICAL"
    elif score >= 0.5:
        return "HIGH"
    elif score >= 0.3:
        return "MEDIUM"
    else:
        return "LOW"


def get_risk_color(level: str) -> str:
    """Get color hex for risk level."""
    return RISK_COLORS.get(level.upper(), "#9ca3af")


def risk_to_geojson_feature(
    risk_data: Dict,
    geometry_data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Convert a risk score record to a GeoJSON Feature.
    
    Args:
        risk_data: Risk score document from database
        geometry_data: Optional geometry data for the region
        
    Returns:
        GeoJSON Feature dictionary
    """
    region_id = risk_data.get("region_id", "UNKNOWN")
    risk_score = risk_data.get("risk_score", 0)
    risk_level = risk_data.get("risk_level") or get_risk_level(risk_score)
    
    # Get geometry from state data or provided geometry
    state_info = INDIA_STATE_GEOMETRIES.get(region_id, {})
    
    if geometry_data:
        geometry = geometry_data
    elif state_info.get("type") == "Polygon":
        geometry = {
            "type": "Polygon",
            "coordinates": state_info["coordinates"]
        }
    elif state_info.get("center"):
        # Use point geometry as fallback
        geometry = {
            "type": "Point",
            "coordinates": state_info["center"]
        }
    else:
        # Default center of India
        geometry = {
            "type": "Point",
            "coordinates": [78.96, 20.59]
        }
    
    return {
        "type": "Feature",
        "properties": {
            "region_id": region_id,
            "region_name": state_info.get("name", region_id),
            "risk_score": round(risk_score, 3),
            "risk_level": risk_level,
            "risk_color": get_risk_color(risk_level),
            "disease": risk_data.get("disease", "ALL"),
            "date": risk_data.get("date", str(date.today())),
            "drivers": risk_data.get("drivers", []),
        },
        "geometry": geometry
    }


def get_risk_geojson(
    target_date: Optional[str] = None,
    disease: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get risk scores as GeoJSON FeatureCollection.
    
    Args:
        target_date: Date for risk scores (ISO format)
        disease: Filter by disease type
        
    Returns:
        GeoJSON FeatureCollection
    """
    try:
        db = get_db()
        risk_col = db["risk_scores"]
        
        # Build filter
        query: Dict[str, Any] = {}
        if disease:
            query["disease"] = disease.upper()
        if target_date:
            query["date"] = target_date
        
        # Get latest date if not specified
        if not target_date:
            latest = risk_col.find_one(query, sort=[("date", -1)])
            if latest:
                target_date = latest.get("date")
                query["date"] = target_date
        
        # Fetch risk scores
        risk_scores = list(risk_col.find(query))
        
        # Convert to GeoJSON features
        features = []
        for risk in risk_scores:
            feature = risk_to_geojson_feature(risk)
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "date": target_date,
                "disease": disease or "ALL",
                "count": len(features)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating risk GeoJSON: {e}")
        return {
            "type": "FeatureCollection",
            "features": [],
            "metadata": {"error": str(e)}
        }


def get_region_boundaries() -> Dict[str, Any]:
    """
    Get region boundary data as GeoJSON.
    Returns point geometries for India states.
    
    Returns:
        GeoJSON FeatureCollection with region boundaries
    """
    features = []
    
    for region_id, info in INDIA_STATE_GEOMETRIES.items():
        feature = {
            "type": "Feature",
            "properties": {
                "region_id": region_id,
                "region_name": info.get("name", region_id)
            },
            "geometry": {
                "type": "Point",
                "coordinates": info.get("center", [78.96, 20.59])
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }
