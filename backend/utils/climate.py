"""
Climate Risk Module
-------------------
Provides weather-aware risk multipliers for disease surveillance.

This module implements climate-based risk adjustments for vector-borne diseases
like dengue, which show strong seasonal patterns aligned with monsoon rainfall.
"""

from typing import Dict, Tuple
from datetime import datetime


# Monsoon Season Risk Multipliers (based on India rainfall patterns)
# These multipliers represent relative disease transmission risk by month
MONSOON_RISK_MULTIPLIERS = {
    # Winter (Low transmission - dry, cool)
    1: 0.5,   # January   - Low risk (post-winter)
    2: 0.5,   # February  - Low risk (pre-monsoon dry)
    
    # Pre-monsoon (Rising transmission - warming, occasional showers)
    3: 0.7,   # March     - Moderate-low risk
    4: 0.8,   # April     - Moderate risk (warming begins)
    5: 1.0,   # May       - Baseline risk (pre-monsoon heat)
    
    # Monsoon (PEAK transmission - heavy rainfall, high humidity)
    6: 1.5,   # June      - High risk (monsoon onset) 🌧️
    7: 1.8,   # July      - Very high risk (monsoon peak) 🌧️
    8: 1.7,   # August    - Very high risk (monsoon continues) 🌧️
    9: 1.5,   # September - High risk (late monsoon) 🌧️
    
    # Post-monsoon (Elevated transmission - standing water, high humidity)
    10: 1.2,  # October   - Elevated risk (post-monsoon humidity)
    11: 0.8,  # November  - Moderate risk (drying out)
    
    # Early winter (Low transmission - cool, dry)
    12: 0.6   # December  - Low-moderate risk (winter onset)
}


# Regional climate modifiers (future enhancement)
# Different regions may have different monsoon patterns
REGIONAL_CLIMATE_ZONES = {
    # North India - Late monsoon arrival
    "IN-DL": "north",   # Delhi
    "IN-HR": "north",   # Haryana
    "IN-PB": "north",   # Punjab
    "IN-UP": "north",   # Uttar Pradesh
    "IN-RJ": "north",   # Rajasthan
    
    # South India - Early monsoon arrival, longer season
    "IN-KA": "south",   # Karnataka
    "IN-TN": "south",   # Tamil Nadu
    "IN-KL": "south",   # Kerala
    "IN-AP": "south",   # Andhra Pradesh
    "IN-TG": "south",   # Telangana
    
    # West Coast - Heavy monsoon
    "IN-MH": "west",    # Maharashtra
    "IN-GA": "west",    # Goa
    
    # East/Northeast - Very heavy monsoon, early arrival
    "IN-WB": "east",    # West Bengal
    "IN-OR": "east",    # Odisha
    "IN-AS": "east",    # Assam
    "IN-MN": "east",    # Manipur
    "IN-NL": "east",    # Nagaland
    
    # Central India
    "IN-MP": "central", # Madhya Pradesh
    "IN-CT": "central", # Chhattisgarh
}


def get_climate_risk_multiplier(date_str: str, region_id: str = None) -> Tuple[float, str]:
    """
    Get climate-based risk multiplier for a given date.
    
    This multiplier represents the relative risk of disease transmission based on
    seasonal weather patterns, primarily monsoon rainfall.
    
    Args:
        date_str: Date in ISO format (YYYY-MM-DD)
        region_id: Optional region ID for regional climate adjustments
        
    Returns:
        Tuple of (multiplier, explanation)
        - multiplier: Float value (0.5 = low risk, 1.8 = very high risk)
        - explanation: String describing the climate period
        
    Example:
        >>> multiplier, explanation = get_climate_risk_multiplier("2021-07-15")
        >>> print(f"{multiplier}: {explanation}")
        1.8: Monsoon peak (July) - Very high transmission risk
    """
    try:
        date = datetime.fromisoformat(date_str)
        month = date.month
        
        multiplier = MONSOON_RISK_MULTIPLIERS.get(month, 1.0)
        
        # Generate explanation based on season
        if month in [6, 7, 8, 9]:
            season = "Monsoon"
            if month == 7:
                risk_desc = "peak"
            elif month in [6, 8]:
                risk_desc = "active"
            else:
                risk_desc = "late phase"
        elif month in [10, 11]:
            season = "Post-monsoon"
            risk_desc = "elevated humidity"
        elif month in [3, 4, 5]:
            season = "Pre-monsoon"
            risk_desc = "warming phase"
        else:
            season = "Winter"
            risk_desc = "low transmission"
        
        # Map multiplier to risk level
        if multiplier >= 1.5:
            risk_level = "Very high"
        elif multiplier >= 1.2:
            risk_level = "High"
        elif multiplier >= 0.8:
            risk_level = "Moderate"
        else:
            risk_level = "Low"
        
        month_names = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }
        
        explanation = f"{season} ({month_names[month]}) - {risk_level} transmission risk"
        
        return multiplier, explanation
        
    except Exception as e:
        # Fallback to baseline risk if date parsing fails
        return 1.0, f"Error parsing date: {e}"


def get_seasonal_context(date_str: str) -> Dict:
    """
    Get comprehensive seasonal context for a date.
    
    Args:
        date_str: Date in ISO format (YYYY-MM-DD)
        
    Returns:
        Dictionary with seasonal information
    """
    try:
        date = datetime.fromisoformat(date_str)
        month = date.month
        
        multiplier = MONSOON_RISK_MULTIPLIERS.get(month, 1.0)
        
        is_monsoon = month in [6, 7, 8, 9]
        is_peak_monsoon = month in [7, 8]
        is_post_monsoon = month in [10, 11]
        is_pre_monsoon = month in [3, 4, 5]
        
        return {
            "month": month,
            "climate_multiplier": multiplier,
            "is_monsoon": is_monsoon,
            "is_peak_monsoon": is_peak_monsoon,
            "is_post_monsoon": is_post_monsoon,
            "is_pre_monsoon": is_pre_monsoon,
            "season": "monsoon" if is_monsoon else "post_monsoon" if is_post_monsoon else "pre_monsoon" if is_pre_monsoon else "winter"
        }
    except Exception as e:
        return {
            "month": 0,
            "climate_multiplier": 1.0,
            "is_monsoon": False,
            "is_peak_monsoon": False,
            "is_post_monsoon": False,
            "is_pre_monsoon": False,
            "season": "unknown",
            "error": str(e)
        }


def calculate_weather_aware_risk(base_risk: float, date_str: str, region_id: str = None) -> Tuple[float, str, Dict]:
    """
    Calculate weather-aware risk by applying climate multiplier to base risk.
    
    Args:
        base_risk: Base risk score (0.0 to 1.0)
        date_str: Date in ISO format
        region_id: Optional region ID for regional adjustments
        
    Returns:
        Tuple of (adjusted_risk, explanation, climate_context)
    """
    climate_multiplier, climate_explanation = get_climate_risk_multiplier(date_str, region_id)
    seasonal_context = get_seasonal_context(date_str)
    
    # Apply multiplier but keep within [0, 1] range
    adjusted_risk = min(1.0, base_risk * climate_multiplier)
    
    # Calculate boost percentage
    boost_pct = ((adjusted_risk - base_risk) / base_risk * 100) if base_risk > 0 else 0
    
    if boost_pct > 10:
        explanation = f"Climate boost: +{boost_pct:.0f}% ({climate_explanation})"
    elif boost_pct < -10:
        explanation = f"Climate reduction: {boost_pct:.0f}% ({climate_explanation})"
    else:
        explanation = f"Neutral climate impact ({climate_explanation})"
    
    return adjusted_risk, explanation, seasonal_context
