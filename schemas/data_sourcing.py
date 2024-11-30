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
    timestamp: datetime
    open: float = Field(..., alias="open_price")
    high: float = Field(..., alias="high_price")
    low: float = Field(..., alias="low_price")
    close: float = Field(..., alias="close_price")
    volume: float
    additional_data: Optional[Dict] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class DataFetchResponse(BaseModel):
    """
    Response schema for fetched market data
    Format: {symbol: {interval: [data_points]}}
    """
    crew_id: int
    status: str
    data_points: Dict[str, Dict[str, List[DataPoint]]]

    model_config = ConfigDict(from_attributes=True)
