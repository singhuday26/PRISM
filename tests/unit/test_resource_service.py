
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from backend.services.resources import ResourceService
from backend.schemas.responses import ResourceConfig, ResourceConfigParams

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

def test_get_config_defaults(mock_db):
    # Setup mock to return None
    mock_db.__getitem__.return_value.find_one.return_value = None
    
    with patch("backend.services.resources.get_db", return_value=mock_db):
        service = ResourceService()
        
        config = service.get_config("unknown_disease")
        
        assert config.disease == "unknown_disease"
        assert config.resource_params.hospitalization_rate == 0.1 # Default

def test_predict_demand_math(mock_db):
    # Mock config
    mock_config = {
        "_id": "dengue",
        "name": "Dengue",
        "resource_params": {
            "hospitalization_rate": 0.2,
            "icu_rate": 0.05,
            "avg_stay_days": 5,
            "nurse_ratio": 0.1,
            "oxygen_rate": 0.5
        }
    }
    
    # Mock forecasts
    # 5 days of forecasts with 20 cases each = 100 active cases
    mock_forecasts = [
        {"pred_mean": 20, "date": f"2024-01-{28+i:02d}"} for i in range(5)
    ]
    
    # Configure mocks
    mock_config_col = MagicMock()
    mock_config_col.find_one.return_value = mock_config
    
    mock_forecasts_col = MagicMock()
    mock_forecasts_col.find.return_value = mock_forecasts

    mock_cases_col = MagicMock()
    mock_cases_col.find.return_value = []  # No historical data
    
    mock_db.__getitem__.side_effect = lambda x: {
        "disease_config": mock_config_col,
        "forecasts_daily": mock_forecasts_col,
        "cases_daily": mock_cases_col
    }.get(x, MagicMock())
    
    with patch("backend.services.resources.get_db", return_value=mock_db):
        service = ResourceService()
        
        # Run prediction
        response = service.predict_demand("IN-MH", "2024-02-01", "dengue")
        
        # Verify Math
        # Active Cases = 20 * 5 = 100
        assert response.forecasted_cases == 100
        
        # General Beds = 100 * 0.2 = 20
        assert response.resources.general_beds == 20
        
        # ICU Beds = 100 * 0.05 = 5
        assert response.resources.icu_beds == 5
        
        # Total Hospitalized = 25
        # Nurses = 25 * 0.1 = 2 (int)
        assert response.resources.nurses == 2
        
        # Oxygen = 25 * 0.5 = 12 (int)
        assert response.resources.oxygen_cylinders == 12

