"""Disease configuration and metadata schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class TransmissionMode(str, Enum):
    """Disease transmission modes."""
    VECTOR = "vector"  # Mosquito, tick, etc.
    AIRBORNE = "airborne"  # Respiratory droplets
    WATERBORNE = "waterborne"  # Contaminated water
    CONTACT = "contact"  # Direct person-to-person
    FOODBORNE = "foodborne"  # Contaminated food
    ZOONOTIC = "zoonotic"  # Animal to human


class Severity(str, Enum):
    """Disease severity classification."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class DiseaseProfile(BaseModel):
    """Disease metadata and configuration."""
    disease_id: str = Field(description="Unique disease identifier (uppercase)")
    name: str = Field(description="Human-readable disease name")
    description: str = Field(description="Brief description of the disease")
    transmission_mode: TransmissionMode = Field(description="Primary transmission mode")
    incubation_period_days: int = Field(ge=0, description="Typical incubation period")
    severity: Severity = Field(description="Overall severity classification")
    
    # Risk modeling parameters
    r0_estimate: Optional[float] = Field(None, ge=0, description="Basic reproduction number")
    case_fatality_rate: Optional[float] = Field(None, ge=0, le=1, description="CFR as decimal")
    
    # Climate sensitivity
    temperature_sensitive: bool = Field(default=False, description="Influenced by temperature")
    rainfall_sensitive: bool = Field(default=False, description="Influenced by rainfall")
    humidity_sensitive: bool = Field(default=False, description="Influenced by humidity")
    
    # Alert thresholds
    alert_threshold_multiplier: float = Field(default=1.5, ge=1.0, description="Threshold for alerts vs baseline")
    high_risk_case_threshold: int = Field(default=100, ge=0, description="Absolute case count for high risk")
    
    # Data source metadata
    data_sources: List[str] = Field(default_factory=list, description="Sources of disease data")
    
    # Additional metadata
    icd_code: Optional[str] = Field(None, description="ICD-10 code")
    vaccine_available: bool = Field(default=False, description="Vaccine availability")
    treatment_available: bool = Field(default=True, description="Treatment availability")
    
    class Config:
        use_enum_values = True


class DiseaseRegistry(BaseModel):
    """Registry of all diseases in the system."""
    diseases: Dict[str, DiseaseProfile] = Field(
        default_factory=dict,
        description="Map of disease_id to disease profile"
    )
    
    def add_disease(self, profile: DiseaseProfile) -> None:
        """Add a disease to the registry."""
        self.diseases[profile.disease_id] = profile
    
    def get_disease(self, disease_id: str) -> Optional[DiseaseProfile]:
        """Get disease profile by ID."""
        return self.diseases.get(disease_id.upper())
    
    def list_diseases(self) -> List[str]:
        """List all disease IDs."""
        return list(self.diseases.keys())
    
    def list_by_transmission(self, mode: TransmissionMode) -> List[DiseaseProfile]:
        """List diseases by transmission mode."""
        return [d for d in self.diseases.values() if d.transmission_mode == mode]
    
    def list_by_severity(self, severity: Severity) -> List[DiseaseProfile]:
        """List diseases by severity."""
        return [d for d in self.diseases.values() if d.severity == severity]
