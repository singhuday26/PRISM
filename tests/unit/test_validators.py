"""Unit tests for validation utilities."""
import pytest
from backend.utils.validators import (
    validate_iso_date,
    validate_disease,
    validate_granularity,
    validate_positive_int,
    validate_region_id,
)
from backend.exceptions import (
    DateValidationError,
    DiseaseValidationError,
    GranularityValidationError,
    ValidationError,
)


class TestValidateIsoDate:
    """Tests for validate_iso_date function."""
    
    def test_valid_dates(self, valid_dates):
        """Test that valid dates are returned unchanged."""
        for date_str in valid_dates:
            result = validate_iso_date(date_str)
            assert result == date_str
    
    def test_none_returns_none(self):
        """Test that None input returns None."""
        assert validate_iso_date(None) is None
    
    def test_invalid_format_raises_error(self):
        """Test that invalid format raises DateValidationError."""
        with pytest.raises(DateValidationError) as exc_info:
            validate_iso_date("2021/01/01")
        assert "Invalid date format" in str(exc_info.value)
        assert exc_info.value.field == "date"
    
    def test_invalid_date_raises_error(self):
        """Test that impossible dates raise DateValidationError."""
        with pytest.raises(DateValidationError):
            validate_iso_date("2021-02-30")
    
    def test_non_leap_year_feb_29(self):
        """Test that Feb 29 on non-leap year raises error."""
        with pytest.raises(DateValidationError):
            validate_iso_date("2021-02-29")
    
    def test_exception_has_value(self):
        """Test that exception includes the invalid value."""
        with pytest.raises(DateValidationError) as exc_info:
            validate_iso_date("bad-date")
        assert exc_info.value.value == "bad-date"


class TestValidateDisease:
    """Tests for validate_disease function."""
    
    def test_none_returns_none_by_default(self):
        """Test that None returns None when allowed."""
        assert validate_disease(None) is None
    
    def test_none_raises_when_not_allowed(self):
        """Test that None raises error when not allowed."""
        with pytest.raises(DiseaseValidationError):
            validate_disease(None, allow_none=False)
    
    def test_uppercases_disease(self):
        """Test that disease name is uppercased."""
        assert validate_disease("dengue") == "DENGUE"
        assert validate_disease("Covid") == "COVID"
    
    def test_strips_whitespace(self):
        """Test that whitespace is stripped."""
        assert validate_disease("  dengue  ") == "DENGUE"
    
    def test_validates_against_list(self):
        """Test validation against allowed list."""
        valid_list = ["DENGUE", "COVID"]
        
        assert validate_disease("dengue", valid_diseases=valid_list) == "DENGUE"
        
        with pytest.raises(DiseaseValidationError) as exc_info:
            validate_disease("malaria", valid_diseases=valid_list)
        assert "DENGUE" in str(exc_info.value)
        assert "COVID" in str(exc_info.value)


class TestValidateGranularity:
    """Tests for validate_granularity function."""
    
    def test_valid_granularities(self, valid_granularities):
        """Test that valid granularities are accepted."""
        for gran in valid_granularities:
            result = validate_granularity(gran)
            assert result == gran.lower()
    
    def test_none_uses_default(self):
        """Test that None returns default value."""
        assert validate_granularity(None) == "monthly"
        assert validate_granularity(None, default="weekly") == "weekly"
    
    def test_case_insensitive(self):
        """Test that validation is case-insensitive."""
        assert validate_granularity("MONTHLY") == "monthly"
        assert validate_granularity("Weekly") == "weekly"
    
    def test_invalid_raises_error(self, invalid_granularities):
        """Test that invalid values raise error."""
        for gran in invalid_granularities:
            if gran:  # Skip empty string which is handled differently
                with pytest.raises(GranularityValidationError):
                    validate_granularity(gran)


class TestValidatePositiveInt:
    """Tests for validate_positive_int function."""
    
    def test_valid_positive_int(self):
        """Test that valid integers pass."""
        assert validate_positive_int(5, "test") == 5
        assert validate_positive_int(1, "test") == 1
        assert validate_positive_int(100, "test") == 100
    
    def test_none_returns_default(self):
        """Test that None returns default."""
        assert validate_positive_int(None, "test") is None
        assert validate_positive_int(None, "test", default=10) == 10
    
    def test_below_min_raises_error(self):
        """Test that values below minimum raise error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_int(0, "horizon", min_value=1)
        assert "at least 1" in str(exc_info.value)
        assert exc_info.value.field == "horizon"
    
    def test_above_max_raises_error(self):
        """Test that values above maximum raise error."""
        with pytest.raises(ValidationError) as exc_info:
            validate_positive_int(50, "limit", max_value=30)
        assert "at most 30" in str(exc_info.value)


class TestValidateRegionId:
    """Tests for validate_region_id function."""
    
    def test_none_returns_none(self):
        """Test that None returns None."""
        assert validate_region_id(None) is None
    
    def test_uppercases_and_strips(self):
        """Test that region ID is uppercased and stripped."""
        assert validate_region_id("in-ap") == "IN-AP"
        assert validate_region_id("  IN-AP  ") == "IN-AP"
        assert validate_region_id("in-ka") == "IN-KA"
