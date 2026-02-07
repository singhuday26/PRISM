from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class RiskScore(BaseModel):
    region_id: str = Field(description="Unique region identifier")
    date: str = Field(description="ISO date YYYY-MM-DD")
    risk_score: float = Field(ge=0, le=1, description="Risk score between 0 and 1")
    risk_level: str = Field(description="Risk level: LOW/MEDIUM/HIGH")
    drivers: list[str] = Field(description="List of risk drivers")
    updated_at: datetime = Field(description="Timestamp of last update")
    disease: Optional[str] = Field(default=None, description="Disease identifier")