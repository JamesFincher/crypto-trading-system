from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DataSourceRequest(BaseModel):
    crew_id: int
    source: str  # e.g., "binance_spot", "binance_futures"
    symbols: List[str]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    interval: Optional[str] = "1m"

class DataSourceResponse(BaseModel):
    crew_id: int
    source: str
    status: str
    message: str
    data_points: Optional[int] = None
    processed_symbols: List[str]

class BacktestDataConfig(BaseModel):
    crew_id: int
    start_date: datetime
    end_date: datetime
    symbols: List[str]
    intervals: List[str]
    include_indicators: bool = True
