from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class LogBase(BaseModel):
    crew_id: int
    timestamp: datetime
    profit: float
    message: str

class LogCreate(LogBase):
    pass

class LogResponse(LogBase):
    id: int

    class Config:
        from_attributes = True

class MetricsResponse(BaseModel):
    profit: float
    win_rate: float
    max_drawdown: float
    sharpe_ratio: float

    class Config:
        from_attributes = True
