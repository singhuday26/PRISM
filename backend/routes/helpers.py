"""Shared helpers for route handlers."""
from fastapi import HTTPException, status
from backend.exceptions import PRISMException


def handle_validation_error(e: Exception) -> None:
    """Convert validation exceptions to HTTP 422 responses."""
    if isinstance(e, PRISMException):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.to_dict()
        )
