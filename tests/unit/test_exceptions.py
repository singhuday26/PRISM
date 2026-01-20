"""Unit tests for custom exceptions."""
import pytest
from backend.exceptions import (
    PRISMException,
    ValidationError,
    DateValidationError,
    DiseaseValidationError,
    GranularityValidationError,
    DatabaseError,
    DataNotFoundError,
    ConfigurationError,
    ServiceUnavailableError,
)


class TestPRISMException:
    """Tests for base PRISMException."""
    
    def test_message_stored(self):
        """Test that message is stored correctly."""
        exc = PRISMException("Test message")
        assert exc.message == "Test message"
        assert str(exc) == "Test message"
    
    def test_details_optional(self):
        """Test that details are optional."""
        exc = PRISMException("Test")
        assert exc.details == {}
    
    def test_details_stored(self):
        """Test that details are stored correctly."""
        exc = PRISMException("Test", {"key": "value"})
        assert exc.details == {"key": "value"}
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        exc = PRISMException("Test", {"key": "value"})
        result = exc.to_dict()
        assert result["error"] == "PRISMException"
        assert result["message"] == "Test"
        assert result["details"] == {"key": "value"}
    
    def test_to_dict_without_details(self):
        """Test dictionary conversion without details."""
        exc = PRISMException("Test")
        result = exc.to_dict()
        assert "details" not in result


class TestValidationError:
    """Tests for ValidationError."""
    
    def test_basic_validation_error(self):
        """Test basic validation error."""
        exc = ValidationError("Invalid input")
        assert exc.message == "Invalid input"
        assert exc.field is None
        assert exc.value is None
    
    def test_with_field_and_value(self):
        """Test validation error with field and value."""
        exc = ValidationError("Invalid value", field="age", value=150)
        assert exc.field == "age"
        assert exc.value == 150
        assert exc.details["field"] == "age"
        assert exc.details["value"] == "150"


class TestDateValidationError:
    """Tests for DateValidationError."""
    
    def test_creates_correct_message(self):
        """Test that correct message is generated."""
        exc = DateValidationError("2021/01/01")
        assert "Invalid date format" in exc.message
        assert "2021/01/01" in exc.message
        assert "YYYY-MM-DD" in exc.message
    
    def test_sets_field_to_date(self):
        """Test that field is set to 'date'."""
        exc = DateValidationError("bad")
        assert exc.field == "date"
    
    def test_stores_value(self):
        """Test that value is stored."""
        exc = DateValidationError("bad-date")
        assert exc.value == "bad-date"


class TestDiseaseValidationError:
    """Tests for DiseaseValidationError."""
    
    def test_creates_correct_message(self):
        """Test that correct message is generated."""
        exc = DiseaseValidationError("UNKNOWN")
        assert "Unknown disease" in exc.message
        assert "UNKNOWN" in exc.message
    
    def test_includes_valid_diseases(self):
        """Test that valid diseases are included in message."""
        exc = DiseaseValidationError("BAD", valid_diseases=["DENGUE", "COVID"])
        assert "DENGUE" in exc.message
        assert "COVID" in exc.message
    
    def test_sets_field_to_disease(self):
        """Test that field is set to 'disease'."""
        exc = DiseaseValidationError("bad")
        assert exc.field == "disease"


class TestGranularityValidationError:
    """Tests for GranularityValidationError."""
    
    def test_creates_correct_message(self):
        """Test that correct message is generated."""
        exc = GranularityValidationError("hourly")
        assert "Invalid granularity" in exc.message
        assert "hourly" in exc.message
        assert "yearly" in exc.message
        assert "monthly" in exc.message
        assert "weekly" in exc.message
    
    def test_sets_field_to_granularity(self):
        """Test that field is set to 'granularity'."""
        exc = GranularityValidationError("bad")
        assert exc.field == "granularity"


class TestDatabaseError:
    """Tests for DatabaseError."""
    
    def test_basic_error(self):
        """Test basic database error."""
        exc = DatabaseError("Connection failed")
        assert exc.message == "Connection failed"
        assert exc.operation is None
    
    def test_with_operation(self):
        """Test database error with operation."""
        exc = DatabaseError("Query failed", operation="find")
        assert exc.operation == "find"
        assert exc.details["operation"] == "find"


class TestDataNotFoundError:
    """Tests for DataNotFoundError."""
    
    def test_basic_error(self):
        """Test basic not found error."""
        exc = DataNotFoundError("Region")
        assert "Region not found" in exc.message
        assert exc.resource == "Region"
    
    def test_with_identifier(self):
        """Test not found error with identifier."""
        exc = DataNotFoundError("Region", identifier="IN-AP")
        assert "IN-AP" in exc.message
        assert exc.identifier == "IN-AP"
    
    def test_with_filters(self):
        """Test not found error with filters."""
        exc = DataNotFoundError("Case", filters={"disease": "DENGUE"})
        assert exc.details["filters"] == {"disease": "DENGUE"}


class TestConfigurationError:
    """Tests for ConfigurationError."""
    
    def test_basic_error(self):
        """Test basic configuration error."""
        exc = ConfigurationError("Missing configuration")
        assert exc.message == "Missing configuration"
    
    def test_with_config_key(self):
        """Test configuration error with key."""
        exc = ConfigurationError("Invalid value", config_key="MONGO_URI")
        assert exc.config_key == "MONGO_URI"
        assert exc.details["config_key"] == "MONGO_URI"


class TestServiceUnavailableError:
    """Tests for ServiceUnavailableError."""
    
    def test_basic_error(self):
        """Test basic service unavailable error."""
        exc = ServiceUnavailableError("MongoDB")
        assert "MongoDB" in exc.message
        assert exc.service == "MongoDB"
    
    def test_with_reason(self):
        """Test service unavailable error with reason."""
        exc = ServiceUnavailableError("MongoDB", reason="Connection timeout")
        assert "Connection timeout" in exc.message
        assert exc.reason == "Connection timeout"
