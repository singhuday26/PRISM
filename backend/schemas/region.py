from pydantic import BaseModel, Field


class Region(BaseModel):
    region_id: str = Field(description="Unique region identifier")
    region_name: str = Field(description="Human readable name")
