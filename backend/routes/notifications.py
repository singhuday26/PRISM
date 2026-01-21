"""
Notification subscription API routes.
"""
import logging
import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field

from backend.db import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class SubscribeRequest(BaseModel):
    """Request body for subscribing to notifications."""
    email: EmailStr
    regions: list[str] = Field(default_factory=list, description="Region IDs to monitor (empty = all)")
    diseases: list[str] = Field(default_factory=list, description="Diseases to monitor (empty = all)")
    frequency: str = Field("immediate", description="Notification frequency: immediate or daily")
    min_risk_level: str = Field("HIGH", description="Minimum risk level: MEDIUM, HIGH, or CRITICAL")


class SubscribeResponse(BaseModel):
    """Response for successful subscription."""
    message: str
    subscriber_id: str
    email: str


class UnsubscribeResponse(BaseModel):
    """Response for successful unsubscription."""
    message: str


class PreferencesResponse(BaseModel):
    """Response with subscriber preferences."""
    email: str
    regions: list[str]
    diseases: list[str]
    frequency: str
    min_risk_level: str
    active: bool


@router.post("/subscribe", response_model=SubscribeResponse, status_code=status.HTTP_201_CREATED)
def subscribe(request: SubscribeRequest):
    """
    Subscribe to email notifications for disease alerts.
    
    Args:
        request: Subscription preferences
        
    Returns:
        Subscriber ID and confirmation message
    """
    try:
        db = get_db()
        subscribers_col = db["subscribers"]
        
        # Check if already subscribed
        existing = subscribers_col.find_one({"email": request.email})
        
        if existing:
            # Update existing subscription
            unsubscribe_token = existing.get("unsubscribe_token", str(uuid.uuid4()))
            
            subscribers_col.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "regions": request.regions,
                        "diseases": request.diseases,
                        "frequency": request.frequency,
                        "min_risk_level": request.min_risk_level.upper(),
                        "active": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return SubscribeResponse(
                message="Subscription updated successfully",
                subscriber_id=str(existing["_id"]),
                email=request.email
            )
        else:
            # Create new subscription
            unsubscribe_token = str(uuid.uuid4())
            
            subscriber_doc = {
                "email": request.email,
                "regions": request.regions,
                "diseases": request.diseases,
                "frequency": request.frequency,
                "min_risk_level": request.min_risk_level.upper(),
                "active": True,
                "unsubscribe_token": unsubscribe_token,
                "created_at": datetime.utcnow(),
                "last_notified_at": None
            }
            
            result = subscribers_col.insert_one(subscriber_doc)
            
            logger.info(f"New subscriber: {request.email}")
            
            return SubscribeResponse(
                message="Subscribed successfully",
                subscriber_id=str(result.inserted_id),
                email=request.email
            )
            
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.delete("/unsubscribe", response_model=UnsubscribeResponse)
def unsubscribe(token: str = Query(..., description="Unsubscribe token from email")):
    """
    Unsubscribe from email notifications.
    
    Args:
        token: Unsubscribe token from email link
        
    Returns:
        Confirmation message
    """
    try:
        db = get_db()
        subscribers_col = db["subscribers"]
        
        # Find and deactivate subscriber
        result = subscribers_col.update_one(
            {"unsubscribe_token": token},
            {"$set": {"active": False, "unsubscribed_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid unsubscribe token"
            )
        
        logger.info(f"Unsubscribed token: {token[:8]}...")
        
        return UnsubscribeResponse(message="Unsubscribed successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unsubscribing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unsubscribe: {str(e)}"
        )


@router.get("/preferences", response_model=PreferencesResponse)
def get_preferences(email: str = Query(..., description="Email address")):
    """
    Get notification preferences for an email address.
    
    Args:
        email: Email address to look up
        
    Returns:
        Subscriber preferences
    """
    try:
        db = get_db()
        subscribers_col = db["subscribers"]
        
        subscriber = subscribers_col.find_one({"email": email})
        
        if not subscriber:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found for this email"
            )
        
        return PreferencesResponse(
            email=subscriber.get("email"),
            regions=subscriber.get("regions", []),
            diseases=subscriber.get("diseases", []),
            frequency=subscriber.get("frequency", "immediate"),
            min_risk_level=subscriber.get("min_risk_level", "HIGH"),
            active=subscriber.get("active", False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preferences: {str(e)}"
        )
