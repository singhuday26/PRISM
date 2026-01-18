from pydantic import BaseModel, Field
from datetime import datetime


class ForecastDaily(BaseModel):
    region_id: str = Field(description="Unique region identifier")
    date: str = Field(description="ISO date YYYY-MM-DD")
    pred_mean: float = Field(description="Predicted mean value")
    pred_lower: float = Field(description="Predicted lower bound")
    pred_upper: float = Field(description="Predicted upper bound")
    model_version: str = Field(description="Version of the forecasting model")
    generated_at: datetime = Field(description="Timestamp when forecast was generated")