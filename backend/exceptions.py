"""Custom exception classes for PRISM application."""
from typing import Optional, Any, Dict


class PRISMException(Exception):
    """Base exception for all PRISM application errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        result = {"error": self.__class__.__name__, "message": self.message}
        if self.details:
            result["details"] = self.details
        return result


class ValidationError(PRISMException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, details)
        self.field = field
        self.value = value


class DateValidationError(ValidationError):
    """Raised when date format is invalid."""
    
    def __init__(self, date_string: str, expected_format: str = "YYYY-MM-DD"):
        super().__init__(
            message=f"Invalid date format: '{date_string}'. Expected {expected_format}.",
            field="date",
            value=date_string
        )


class DiseaseValidationError(ValidationError):
    """Raised when disease type is invalid."""
    
    def __init__(self, disease: str, valid_diseases: Optional[list] = None):
        msg = f"Unknown disease: '{disease}'."
        if valid_diseases:
            msg += f" Valid options: {', '.join(valid_diseases)}."
        super().__init__(message=msg, field="disease", value=disease)
        self.valid_diseases = valid_diseases


class GranularityValidationError(ValidationError):
    """Raised when granularity type is invalid."""
    
    VALID_GRANULARITIES = ["yearly", "monthly", "weekly"]
    
    def __init__(self, granularity: str):
        super().__init__(
            message=f"Invalid granularity: '{granularity}'. Must be one of: {', '.join(self.VALID_GRANULARITIES)}.",
            field="granularity",
            value=granularity
        )


class DatabaseError(PRISMException):
    """Raised when a database operation fails."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        details = {}
        if operation:
            details["operation"] = operation
        super().__init__(message, details)
        self.operation = operation


class DataNotFoundError(PRISMException):
    """Raised when requested data is not found."""
    
    def __init__(
        self, 
        resource: str, 
        identifier: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ):
        details = {"resource": resource}
        if identifier:
            details["identifier"] = identifier
        if filters:
            details["filters"] = filters
        
        msg = f"{resource} not found"
        if identifier:
            msg += f": {identifier}"
        
        super().__init__(msg, details)
        self.resource = resource
        self.identifier = identifier


class ConfigurationError(PRISMException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, details)
        self.config_key = config_key


class ServiceUnavailableError(PRISMException):
    """Raised when a required service is unavailable."""
    
    def __init__(self, service: str, reason: Optional[str] = None):
        msg = f"Service unavailable: {service}"
        if reason:
            msg += f". Reason: {reason}"
        super().__init__(msg, {"service": service})
        self.service = service
        self.reason = reason
