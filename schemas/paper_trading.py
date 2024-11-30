from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TradeStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class TradeSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class StrategyConfig(BaseModel):
    type: str
    parameters: Dict[str, Any]

class PaperTradingSessionBase(BaseModel):
    name: str
    strategy_config: StrategyConfig
    trading_pairs: List[str]
    risk_percentage: float = Field(..., gt=0, le=100)
    initial_balance: float = Field(..., gt=0)
    max_position_size: float = Field(..., gt=0)

class PaperTradingSessionCreate(PaperTradingSessionBase):
    pass

class PaperTradingSessionResponse(PaperTradingSessionBase):
    id: int
    current_balance: float
    total_pnl: float
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PaperTradeBase(BaseModel):
    session_id: int
    symbol: str
    entry_price: float = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    side: TradeSide
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class PaperTradeCreate(PaperTradeBase):
    pass

class PaperTradeResponse(PaperTradeBase):
    id: int
    exit_price: Optional[float] = None
    status: TradeStatus
    entry_time: datetime
    exit_time: Optional[datetime] = None
    realized_pnl: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    roi_percentage: Optional[float] = None

    class Config:
        orm_mode = True

class PerformanceMetrics(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_roi_percentage: float
    sharpe_ratio: float
    max_drawdown: float
    avg_trade_duration: float
    best_trade_roi: float
    worst_trade_roi: float
    current_drawdown: float
    risk_reward_ratio: float
    profit_factor: float
    avg_win_size: float
    avg_loss_size: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    recovery_factor: float
