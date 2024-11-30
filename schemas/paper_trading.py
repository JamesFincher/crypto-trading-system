from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaperTradeBase(BaseModel):
    trading_crew_id: int
    symbol: str
    entry_price: float
    quantity: float
    side: str

class PaperTradeCreate(PaperTradeBase):
    pass

class PaperTradeResponse(PaperTradeBase):
    id: int
    exit_price: Optional[float] = None
    status: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    pnl: Optional[float] = None

    class Config:
        orm_mode = True

class PerformanceMetrics(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    sharpe_ratio: float
    max_drawdown: float
    avg_trade_duration: float
