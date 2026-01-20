"""Centralized validation utilities for PRISM application."""
import re
from datetime import datetime
from typing import Optional, List, Literal

from backend.exceptions import (
    DateValidationError,
    DiseaseValidationError,
    GranularityValidationError,
)

# Valid granularity types
GranularityType = Literal["yearly", "monthly", "weekly"]
VALID_GRANULARITIES: List[str] = ["yearly", "monthly", "weekly"]

# ISO date pattern
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_iso_date(date_str: Optional[str]) -> Optional[str]:
    """
    Validate ISO date format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate, or None
        
    Returns:
        The validated date string, or None if input was None
        
    Raises:
        DateValidationError: If date format is invalid
    """
    if date_str is None:
        return None
    
    # Check pattern first for better error messages
    if not ISO_DATE_PATTERN.match(date_str):
        raise DateValidationError(date_str)
    
    # Validate it's a real date (e.g., not 2021-02-30)
    try:
        datetime.fromisoformat(date_str)
        return date_str
    except ValueError:
        raise DateValidationError(date_str)


def validate_disease(
    disease: Optional[str], 
    valid_diseases: Optional[List[str]] = None,
    allow_none: bool = True
) -> Optional[str]:
    """
    Validate disease type.
    
    Args:
        disease: Disease string to validate
        valid_diseases: Optional list of valid disease names
        allow_none: Whether None is a valid input
        
    Returns:
        The validated disease string (uppercased), or None
        
    Raises:
        DiseaseValidationError: If disease is not in valid list
    """
    if disease is None:
        if allow_none:
            return None
        raise DiseaseValidationError("None", valid_diseases)
    
    normalized = disease.upper().strip()
    
    if valid_diseases and normalized not in [d.upper() for d in valid_diseases]:
        raise DiseaseValidationError(disease, valid_diseases)
    
    return normalized


def validate_granularity(
    granularity: Optional[str],
    default: GranularityType = "monthly"
) -> GranularityType:
    """
    Validate granularity type.
    
    Args:
        granularity: Granularity string to validate
        default: Default value if granularity is None
        
    Returns:
        The validated granularity string
        
    Raises:
        GranularityValidationError: If granularity is invalid
    """
    if granularity is None:
        return default
    
    normalized = granularity.lower().strip()
    
    if normalized not in VALID_GRANULARITIES:
        raise GranularityValidationError(granularity)
    
    return normalized  # type: ignore


def validate_positive_int(
    value: Optional[int],
    field_name: str,
    min_value: int = 1,
    max_value: Optional[int] = None,
    default: Optional[int] = None
) -> Optional[int]:
    """
    Validate that an integer is positive and within bounds.
    
    Args:
        value: Integer to validate
        field_name: Name of field for error messages
        min_value: Minimum allowed value
        max_value: Maximum allowed value (optional)
        default: Default value if input is None
        
    Returns:
        The validated integer, or default if input was None
        
    Raises:
        ValidationError: If value is out of bounds
    """
    from backend.exceptions import ValidationError
    
    if value is None:
        return default
    
    if value < min_value:
        raise ValidationError(
            f"{field_name} must be at least {min_value}, got {value}",
            field=field_name,
            value=value
        )
    
    if max_value is not None and value > max_value:
        raise ValidationError(
            f"{field_name} must be at most {max_value}, got {value}",
            field=field_name,
            value=value
        )
    
    return value


def validate_region_id(region_id: Optional[str]) -> Optional[str]:
    """
    Validate region ID format.
    
    Args:
        region_id: Region ID to validate
        
    Returns:
        The validated region ID (stripped), or None
    """
    if region_id is None:
        return None
    
    return region_id.strip().upper()
