from pydantic import BaseModel, Field
from typing import Optional


class CaseDaily(BaseModel):
    region_id: str = Field(description="Unique region identifier")
    date: str = Field(description="ISO date YYYY-MM-DD")
    confirmed: int = Field(ge=0)
    deaths: int = Field(ge=0)
    recovered: int = Field(ge=0)
    disease: Optional[str] = Field(default=None, description="Disease identifier (e.g., DENGUE, COVID)")
