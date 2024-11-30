from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class TradingCrewBase(BaseModel):
    name: str
    strategy_config: Dict
    max_position_size: float
    risk_percentage: float
    trading_pairs: List[str]

class TradingCrewCreate(TradingCrewBase):
    pass

class TradingCrewResponse(TradingCrewBase):
    id: int
    is_active: bool
    user_id: int

    class Config:
        orm_mode = True

class TradeBase(BaseModel):
    symbol: str
    side: str
    quantity: float
    price: float
    timestamp: datetime

class TradeCreate(TradeBase):
    pass

class TradeResponse(TradeBase):
    id: int
    status: str
    pnl: Optional[float] = None

    class Config:
        orm_mode = True
