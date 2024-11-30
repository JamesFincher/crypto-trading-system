from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class LogBase(BaseModel):
    trading_crew_id: int
    timestamp: datetime
    log_type: str
    message: str

class LogCreate(LogBase):
    metrics: Dict = {}
    pnl: Optional[float] = None
    win_rate: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None

class LogResponse(LogBase):
    id: int
    metrics: Dict
    pnl: Optional[float] = None
    win_rate: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None

    class Config:
        orm_mode = True

class MetricsRequest(BaseModel):
    crew_id: int
    metric_type: str  # e.g., "performance", "risk", "execution"
    timeframe: str  # e.g., "1d", "1w", "1m"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
