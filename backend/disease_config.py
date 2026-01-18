"""Pre-configured disease profiles for common diseases."""
from backend.schemas.disease import (
    DiseaseProfile, 
    DiseaseRegistry,
    TransmissionMode,
    Severity
)


def get_default_disease_registry() -> DiseaseRegistry:
    """Create registry with pre-configured disease profiles."""
    registry = DiseaseRegistry()
    
    # Dengue Fever
    registry.add_disease(DiseaseProfile(
        disease_id="DENGUE",
        name="Dengue Fever",
        description="Mosquito-borne viral disease causing fever, rash, and joint pain",
        transmission_mode=TransmissionMode.VECTOR,
        incubation_period_days=7,
        severity=Severity.MODERATE,
        r0_estimate=2.5,
        case_fatality_rate=0.01,
        temperature_sensitive=True,
        rainfall_sensitive=True,
        humidity_sensitive=True,
        alert_threshold_multiplier=1.5,
        high_risk_case_threshold=100,
        data_sources=["National Vector Borne Disease Control Programme (NVBDCP)"],
        icd_code="A90",
        vaccine_available=True,
        treatment_available=True
    ))
    
    # COVID-19
    registry.add_disease(DiseaseProfile(
        disease_id="COVID",
        name="COVID-19",
        description="Respiratory illness caused by SARS-CoV-2 virus",
        transmission_mode=TransmissionMode.AIRBORNE,
        incubation_period_days=5,
        severity=Severity.HIGH,
        r0_estimate=5.0,
        case_fatality_rate=0.02,
        temperature_sensitive=True,
        rainfall_sensitive=False,
        humidity_sensitive=True,
        alert_threshold_multiplier=1.3,
        high_risk_case_threshold=500,
        data_sources=["WHO COVID-19 Database", "Johns Hopkins CSSE"],
        icd_code="U07.1",
        vaccine_available=True,
        treatment_available=True
    ))
    
    # Malaria
    registry.add_disease(DiseaseProfile(
        disease_id="MALARIA",
        name="Malaria",
        description="Mosquito-borne parasitic disease causing fever and chills",
        transmission_mode=TransmissionMode.VECTOR,
        incubation_period_days=14,
        severity=Severity.HIGH,
        r0_estimate=1.5,
        case_fatality_rate=0.003,
        temperature_sensitive=True,
        rainfall_sensitive=True,
        humidity_sensitive=True,
        alert_threshold_multiplier=1.4,
        high_risk_case_threshold=150,
        data_sources=["National Vector Borne Disease Control Programme (NVBDCP)"],
        icd_code="B50-B54",
        vaccine_available=True,
        treatment_available=True
    ))
    
    # Tuberculosis
    registry.add_disease(DiseaseProfile(
        disease_id="TUBERCULOSIS",
        name="Tuberculosis (TB)",
        description="Bacterial infection primarily affecting the lungs",
        transmission_mode=TransmissionMode.AIRBORNE,
        incubation_period_days=90,
        severity=Severity.HIGH,
        r0_estimate=10.0,
        case_fatality_rate=0.15,
        temperature_sensitive=False,
        rainfall_sensitive=False,
        humidity_sensitive=True,
        alert_threshold_multiplier=1.2,
        high_risk_case_threshold=50,
        data_sources=["National TB Elimination Programme (NTEP)"],
        icd_code="A15-A19",
        vaccine_available=True,
        treatment_available=True
    ))
    
    # Influenza
    registry.add_disease(DiseaseProfile(
        disease_id="INFLUENZA",
        name="Influenza (Flu)",
        description="Seasonal respiratory illness caused by influenza viruses",
        transmission_mode=TransmissionMode.AIRBORNE,
        incubation_period_days=2,
        severity=Severity.MODERATE,
        r0_estimate=1.3,
        case_fatality_rate=0.001,
        temperature_sensitive=True,
        rainfall_sensitive=False,
        humidity_sensitive=True,
        alert_threshold_multiplier=1.5,
        high_risk_case_threshold=200,
        data_sources=["WHO FluNet", "National Influenza Surveillance"],
        icd_code="J09-J11",
        vaccine_available=True,
        treatment_available=True
    ))
    
    # Cholera
    registry.add_disease(DiseaseProfile(
        disease_id="CHOLERA",
        name="Cholera",
        description="Bacterial waterborne disease causing severe diarrhea",
        transmission_mode=TransmissionMode.WATERBORNE,
        incubation_period_days=3,
        severity=Severity.HIGH,
        r0_estimate=2.0,
        case_fatality_rate=0.05,
        temperature_sensitive=True,
        rainfall_sensitive=True,
        humidity_sensitive=False,
        alert_threshold_multiplier=1.3,
        high_risk_case_threshold=50,
        data_sources=["Integrated Disease Surveillance Programme (IDSP)"],
        icd_code="A00",
        vaccine_available=True,
        treatment_available=True
    ))
    
    # Chikungunya
    registry.add_disease(DiseaseProfile(
        disease_id="CHIKUNGUNYA",
        name="Chikungunya",
        description="Mosquito-borne viral disease causing fever and severe joint pain",
        transmission_mode=TransmissionMode.VECTOR,
        incubation_period_days=5,
        severity=Severity.MODERATE,
        r0_estimate=3.0,
        case_fatality_rate=0.001,
        temperature_sensitive=True,
        rainfall_sensitive=True,
        humidity_sensitive=True,
        alert_threshold_multiplier=1.5,
        high_risk_case_threshold=100,
        data_sources=["National Vector Borne Disease Control Programme (NVBDCP)"],
        icd_code="A92.0",
        vaccine_available=False,
        treatment_available=True
    ))
    
    # Typhoid
    registry.add_disease(DiseaseProfile(
        disease_id="TYPHOID",
        name="Typhoid Fever",
        description="Bacterial infection spread through contaminated food and water",
        transmission_mode=TransmissionMode.WATERBORNE,
        incubation_period_days=14,
        severity=Severity.MODERATE,
        r0_estimate=2.5,
        case_fatality_rate=0.01,
        temperature_sensitive=True,
        rainfall_sensitive=True,
        humidity_sensitive=False,
        alert_threshold_multiplier=1.4,
        high_risk_case_threshold=75,
        data_sources=["Integrated Disease Surveillance Programme (IDSP)"],
        icd_code="A01.0",
        vaccine_available=True,
        treatment_available=True
    ))
    
    # Japanese Encephalitis
    registry.add_disease(DiseaseProfile(
        disease_id="JAPANESE_ENCEPHALITIS",
        name="Japanese Encephalitis",
        description="Mosquito-borne viral brain infection",
        transmission_mode=TransmissionMode.VECTOR,
        incubation_period_days=10,
        severity=Severity.CRITICAL,
        r0_estimate=1.5,
        case_fatality_rate=0.30,
        temperature_sensitive=True,
        rainfall_sensitive=True,
        humidity_sensitive=True,
        alert_threshold_multiplier=1.2,
        high_risk_case_threshold=25,
        data_sources=["National Vector Borne Disease Control Programme (NVBDCP)"],
        icd_code="A83.0",
        vaccine_available=True,
        treatment_available=True
    ))
    
    # Measles
    registry.add_disease(DiseaseProfile(
        disease_id="MEASLES",
        name="Measles",
        description="Highly contagious viral disease causing fever and rash",
        transmission_mode=TransmissionMode.AIRBORNE,
        incubation_period_days=14,
        severity=Severity.HIGH,
        r0_estimate=15.0,
        case_fatality_rate=0.002,
        temperature_sensitive=False,
        rainfall_sensitive=False,
        humidity_sensitive=False,
        alert_threshold_multiplier=1.2,
        high_risk_case_threshold=30,
        data_sources=["Integrated Disease Surveillance Programme (IDSP)"],
        icd_code="B05",
        vaccine_available=True,
        treatment_available=True
    ))
    
    return registry


# Global registry instance
DISEASE_REGISTRY = get_default_disease_registry()


def get_disease_registry() -> DiseaseRegistry:
    """Get the global disease registry."""
    return DISEASE_REGISTRY
