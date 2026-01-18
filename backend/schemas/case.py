from pydantic import BaseModel, Field


class CaseDaily(BaseModel):
    region_id: str = Field(description="Unique region identifier")
    date: str = Field(description="ISO date YYYY-MM-DD")
    confirmed: int = Field(ge=0)
    deaths: int = Field(ge=0)
    recovered: int = Field(ge=0)
