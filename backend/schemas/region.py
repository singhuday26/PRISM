from pydantic import BaseModel, Field
from typing import Optional


class Region(BaseModel):
    region_id: str = Field(description="Unique region identifier")
    region_name: str = Field(description="Human readable name")
    disease: Optional[str] = Field(default=None, description="Disease-specific region metadata (null = disease-agnostic)")
