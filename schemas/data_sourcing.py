from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional
from datetime import datetime

class DataFetchRequest(BaseModel):
    """
    Request schema for fetching market data
    """
    crew_id: int = Field(..., description="ID of the trading crew")
    start_time: int = Field(..., description="Start timestamp in milliseconds")
    end_time: int = Field(..., description="End timestamp in milliseconds")
    intervals: List[str] = Field(..., description="List of time intervals (e.g., ['1h', '4h'])")

    model_config = ConfigDict(from_attributes=True)


class DataPoint(BaseModel):
    """
    Schema for a single market data point
    """
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    model_config = ConfigDict(from_attributes=True)


class DataFetchResponse(BaseModel):
    """
    Response schema for fetched market data
    """
    crew_id: int
    status: str
    data_points: Dict[str, Dict[str, List[DataPoint]]]  # symbol -> interval -> data points

    model_config = ConfigDict(from_attributes=True)
