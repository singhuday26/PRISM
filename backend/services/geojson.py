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
INDIA_STATE_GEOMETRIES = {
    "IN-AP": {"name": "Andhra Pradesh", "center": [79.74, 15.91], "type": "Point"},
    "IN-AR": {"name": "Arunachal Pradesh", "center": [94.72, 28.22], "type": "Point"},
    "IN-AS": {"name": "Assam", "center": [92.94, 26.20], "type": "Point"},
    "IN-BR": {"name": "Bihar", "center": [85.31, 25.10], "type": "Point"},
    "IN-CT": {"name": "Chhattisgarh", "center": [81.87, 21.27], "type": "Point"},
    "IN-GA": {"name": "Goa", "center": [74.12, 15.30], "type": "Point"},
    "IN-GJ": {"name": "Gujarat", "center": [71.19, 22.26], "type": "Point"},
    "IN-HR": {"name": "Haryana", "center": [76.09, 29.06], "type": "Point"},
    "IN-HP": {"name": "Himachal Pradesh", "center": [77.17, 31.10], "type": "Point"},
    "IN-JH": {"name": "Jharkhand", "center": [85.28, 23.61], "type": "Point"},
    "IN-KA": {"name": "Karnataka", "center": [75.71, 15.32], "type": "Point"},
    "IN-KL": {"name": "Kerala", "center": [76.27, 10.85], "type": "Point"},
    "IN-MP": {"name": "Madhya Pradesh", "center": [78.66, 22.97], "type": "Point"},
    "IN-MH": {"name": "Maharashtra", "center": [75.71, 19.75], "type": "Point"},
    "IN-MN": {"name": "Manipur", "center": [93.91, 24.66], "type": "Point"},
    "IN-ML": {"name": "Meghalaya", "center": [91.37, 25.47], "type": "Point"},
    "IN-MZ": {"name": "Mizoram", "center": [92.94, 23.16], "type": "Point"},
    "IN-NL": {"name": "Nagaland", "center": [94.56, 26.16], "type": "Point"},
    "IN-OR": {"name": "Odisha", "center": [85.09, 20.95], "type": "Point"},
    "IN-PB": {"name": "Punjab", "center": [75.34, 31.15], "type": "Point"},
    "IN-RJ": {"name": "Rajasthan", "center": [74.22, 27.02], "type": "Point"},
    "IN-SK": {"name": "Sikkim", "center": [88.51, 27.53], "type": "Point"},
    "IN-TN": {"name": "Tamil Nadu", "center": [78.66, 11.13], "type": "Point"},
    "IN-TG": {"name": "Telangana", "center": [79.02, 18.11], "type": "Point"},
    "IN-TR": {"name": "Tripura", "center": [91.99, 23.94], "type": "Point"},
    "IN-UP": {"name": "Uttar Pradesh", "center": [80.95, 26.85], "type": "Point"},
    "IN-UK": {"name": "Uttarakhand", "center": [79.02, 30.07], "type": "Point"},
    "IN-WB": {"name": "West Bengal", "center": [87.86, 22.99], "type": "Point"},
    "IN-AN": {"name": "Andaman and Nicobar", "center": [92.62, 11.74], "type": "Point"},
    "IN-CH": {"name": "Chandigarh", "center": [76.77, 30.73], "type": "Point"},
    "IN-DN": {"name": "Dadra and Nagar Haveli", "center": [73.01, 20.19], "type": "Point"},
    "IN-DD": {"name": "Daman and Diu", "center": [72.83, 20.42], "type": "Point"},
    "IN-DL": {"name": "Delhi", "center": [77.10, 28.70], "type": "Point"},
    "IN-JK": {"name": "Jammu and Kashmir", "center": [74.80, 33.78], "type": "Point"},
    "IN-LA": {"name": "Ladakh", "center": [77.58, 34.15], "type": "Point"},
    "IN-LD": {"name": "Lakshadweep", "center": [72.64, 10.57], "type": "Point"},
    "IN-PY": {"name": "Puducherry", "center": [79.81, 11.93], "type": "Point"},
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
            query["disease"] = disease
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
