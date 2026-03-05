"""Pydantic schemas for the Ecosystem Wing."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class InstitutionType(str, Enum):
    HOSPITAL = "hospital"
    AMBULANCE = "ambulance"
    FIRE_STATION = "fire_station"
    LAB = "lab"
    PHARMACY = "pharmacy"
    DISTRICT_ADMIN = "district_admin"
    POLICE = "police"
    BLOOD_BANK = "blood_bank"
    WASH = "wash"
    NGO = "ngo"


class OperationalStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# Status sub-models (per institution type)
# ---------------------------------------------------------------------------

class HospitalStatus(BaseModel):
    beds_total: int = 0
    beds_available: int = 0
    icu_total: int = 0
    icu_available: int = 0
    ventilators_total: int = 0
    ventilators_available: int = 0
    staff_on_duty: int = 0
    oxygen_cylinders: int = 0


class AmbulanceStatus(BaseModel):
    fleet_size: int = 0
    active_vehicles: int = 0
    avg_response_min: float = 0.0
    dispatched: int = 0


class FireStationStatus(BaseModel):
    active_units: int = 0
    total_units: int = 0
    hazmat_available: bool = False
    shelter_capacity: int = 0


class LabStatus(BaseModel):
    daily_capacity: int = 0
    tests_today: int = 0
    backlog: int = 0
    turnaround_hours: float = 0.0
    test_types: List[str] = Field(default_factory=list)


class PharmacyStatus(BaseModel):
    critical_drugs_stock: Dict[str, int] = Field(default_factory=dict)
    stock_health_pct: float = 100.0
    last_restock_date: Optional[str] = None


class DistrictAdminStatus(BaseModel):
    active_directives: int = 0
    evacuation_plan_ready: bool = False
    budget_allocated_lakhs: float = 0.0
    coordination_score: float = 0.0  # 0-100


class PoliceStatus(BaseModel):
    personnel_deployed: int = 0
    checkpoints_active: int = 0
    crowd_control_teams: int = 0
    patrol_vehicles: int = 0


class BloodBankStatus(BaseModel):
    inventory: Dict[str, int] = Field(default_factory=dict)  # e.g. {"A+": 20, "O-": 5}
    units_expiring_soon: int = 0
    demand_today: int = 0


class WashStatus(BaseModel):
    water_quality_index: float = 0.0  # 0-100, higher is better
    sanitation_coverage_pct: float = 0.0
    sewage_surveillance_active: bool = False
    contamination_alerts: int = 0


class NgoStatus(BaseModel):
    volunteers_active: int = 0
    relief_camps: int = 0
    supply_kits_available: int = 0
    beneficiaries_served: int = 0


# ---------------------------------------------------------------------------
# Core models
# ---------------------------------------------------------------------------

class Institution(BaseModel):
    institution_id: str = Field(description="Unique identifier")
    name: str = Field(description="Institution name")
    type: InstitutionType = Field(description="Category of institution")
    region_id: str = Field(description="Region this institution belongs to")
    lat: Optional[float] = None
    lon: Optional[float] = None
    address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: OperationalStatus = OperationalStatus.OPERATIONAL
    health_score: float = Field(default=100.0, ge=0, le=100, description="0-100 health score")
    status_detail: Optional[dict] = Field(default=None, description="Type-specific status detail")
    last_updated: Optional[str] = None


class InstitutionAlert(BaseModel):
    alert_id: str
    institution_id: str
    institution_name: str
    institution_type: InstitutionType
    region_id: str
    severity: AlertSeverity
    message: str
    timestamp: str


class CategorySummary(BaseModel):
    type: InstitutionType
    label: str
    count: int = 0
    operational: int = 0
    degraded: int = 0
    critical: int = 0
    offline: int = 0
    avg_health_score: float = 0.0


class EcosystemSummary(BaseModel):
    total_institutions: int = 0
    overall_health_score: float = 0.0
    active_alerts: int = 0
    categories: List[CategorySummary] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class InstitutionsResponse(BaseModel):
    institutions: List[Institution]
    count: int


class EcosystemSummaryResponse(BaseModel):
    summary: EcosystemSummary
    alerts: List[InstitutionAlert] = Field(default_factory=list)
