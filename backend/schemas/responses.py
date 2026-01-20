"""Pydantic response models for PRISM API endpoints."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Base Response Models
# ============================================================================

class BaseResponse(BaseModel):
    """Base response model with common fields."""
    
    class Config:
        from_attributes = True
        extra = "allow"  # Allow extra fields for forward compatibility


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str = Field(description="Error type/name")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Additional error details"
    )


# ============================================================================
# Health Check Models
# ============================================================================

class CollectionStats(BaseModel):
    """Statistics for a database collection."""
    regions: int = Field(ge=-1, description="Number of region documents")
    cases_daily: int = Field(ge=-1, description="Number of daily case records")
    risk_scores: int = Field(ge=-1, description="Number of risk score records")
    alerts: int = Field(ge=-1, description="Number of alert records")
    forecasts_daily: int = Field(ge=-1, description="Number of forecast records")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(description="Health status: 'healthy' or 'unhealthy'")
    database: str = Field(description="Database name")
    collections: Optional[CollectionStats] = Field(
        default=None, 
        description="Collection statistics (when healthy)"
    )
    ping: Optional[bool] = Field(
        default=None, 
        description="Database ping result"
    )
    error: Optional[str] = Field(
        default=None, 
        description="Error message (when unhealthy)"
    )


# ============================================================================
# Risk Score Models
# ============================================================================

class ClimateInfo(BaseModel):
    """Climate context information for risk scoring."""
    base_risk: float = Field(ge=0, le=1, description="Risk before climate adjustment")
    climate_multiplier: float = Field(description="Climate-based multiplier applied")
    adjusted_risk: float = Field(ge=0, le=1, description="Risk after climate adjustment")
    explanation: str = Field(description="Human-readable explanation")
    season: str = Field(description="Current season")
    is_monsoon: bool = Field(description="Whether it's monsoon season")


class RiskScore(BaseModel):
    """Individual risk score record."""
    region_id: str = Field(description="Unique region identifier")
    date: str = Field(description="Date of risk assessment (YYYY-MM-DD)")
    risk_score: float = Field(ge=0, le=1, description="Computed risk score")
    risk_level: str = Field(description="Risk level: LOW, MEDIUM, or HIGH")
    drivers: List[str] = Field(
        default_factory=list, 
        description="Factors contributing to risk"
    )
    disease: Optional[str] = Field(default=None, description="Disease type")
    climate_info: Optional[ClimateInfo] = Field(
        default=None, 
        description="Climate context if climate boost was applied"
    )


class RiskScoreResponse(BaseModel):
    """Response for risk score endpoints."""
    date: Optional[str] = Field(description="Date of the risk scores")
    risk_scores: List[RiskScore] = Field(description="List of risk score records")
    count: int = Field(ge=0, description="Number of risk scores returned")
    disease: Optional[str] = Field(default=None, description="Disease filter applied")


# ============================================================================
# Alert Models
# ============================================================================

class Alert(BaseModel):
    """Individual alert record."""
    region_id: str = Field(description="Unique region identifier")
    date: str = Field(description="Date of the alert (YYYY-MM-DD)")
    risk_score: float = Field(ge=0, le=1, description="Risk score that triggered alert")
    risk_level: Optional[str] = Field(default=None, description="Risk level")
    reason: str = Field(description="Reason for the alert")
    disease: Optional[str] = Field(default=None, description="Disease type")
    created_at: Optional[datetime] = Field(default=None, description="Alert creation time")


class AlertsResponse(BaseModel):
    """Response for alert endpoints."""
    date: Optional[str] = Field(description="Date of the alerts")
    alerts: List[Alert] = Field(description="List of alert records")
    count: int = Field(ge=0, description="Number of alerts returned")
    disease: Optional[str] = Field(default=None, description="Disease filter applied")


# ============================================================================
# Forecast Models
# ============================================================================

class Forecast(BaseModel):
    """Individual forecast record."""
    region_id: str = Field(description="Unique region identifier")
    date: str = Field(description="Forecast date (YYYY-MM-DD)")
    pred_mean: float = Field(description="Predicted mean value")
    pred_lower: float = Field(description="Lower confidence bound")
    pred_upper: float = Field(description="Upper confidence bound")
    model_version: str = Field(description="Model version used")
    source_granularity: Optional[str] = Field(
        default=None, 
        description="Data granularity used for forecast"
    )
    disease: Optional[str] = Field(default=None, description="Disease type")
    generated_at: Optional[datetime] = Field(
        default=None, 
        description="When forecast was generated"
    )


class ForecastsResponse(BaseModel):
    """Response for forecast endpoints."""
    date: Optional[str] = Field(description="Base date for forecasts")
    forecasts: List[Forecast] = Field(description="List of forecast records")
    count: int = Field(ge=0, description="Number of forecast records")
    disease: Optional[str] = Field(default=None, description="Disease filter applied")
    granularity: Optional[str] = Field(
        default=None, 
        description="Data granularity used"
    )


# ============================================================================
# Region Models
# ============================================================================

class Region(BaseModel):
    """Region information."""
    region_id: str = Field(description="Unique region identifier")
    region_name: Optional[str] = Field(default=None, description="Human-readable name")
    disease: Optional[str] = Field(default=None, description="Disease tracked in region")
    case_count: Optional[int] = Field(
        default=None, 
        ge=0, 
        description="Total case count"
    )


class RegionsResponse(BaseModel):
    """Response for region listing."""
    regions: List[Region] = Field(description="List of regions")
    count: int = Field(ge=0, description="Number of regions")
    disease: Optional[str] = Field(default=None, description="Disease filter applied")


class DiseasesResponse(BaseModel):
    """Response for diseases listing."""
    diseases: List[str] = Field(description="List of available diseases")
    count: int = Field(ge=0, description="Number of diseases")


# ============================================================================
# Hotspot Models
# ============================================================================

class Hotspot(BaseModel):
    """Hotspot region with case counts."""
    region_id: str = Field(description="Unique region identifier")
    region_name: Optional[str] = Field(default=None, description="Human-readable name")
    confirmed_sum: int = Field(ge=0, description="Total confirmed cases")
    deaths_sum: Optional[int] = Field(default=None, ge=0, description="Total deaths")
    disease: Optional[str] = Field(default=None, description="Disease type")


class HotspotsResponse(BaseModel):
    """Response for hotspot endpoints."""
    hotspots: List[Hotspot] = Field(description="List of hotspot regions")
    count: int = Field(ge=0, description="Number of hotspots")
    disease: Optional[str] = Field(default=None, description="Disease filter applied")


# ============================================================================
# Pipeline Models
# ============================================================================

class PipelineStepResult(BaseModel):
    """Result of a single pipeline step."""
    step: str = Field(description="Step name")
    success: bool = Field(description="Whether step succeeded")
    count: int = Field(ge=0, description="Number of records processed")
    date: Optional[str] = Field(default=None, description="Date processed")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class PipelineResponse(BaseModel):
    """Response for pipeline execution."""
    success: bool = Field(description="Whether pipeline completed successfully")
    date: str = Field(description="Date processed")
    steps: List[PipelineStepResult] = Field(description="Results of each step")
    disease: Optional[str] = Field(default=None, description="Disease processed")
    duration_seconds: Optional[float] = Field(
        default=None, 
        description="Total execution time"
    )
