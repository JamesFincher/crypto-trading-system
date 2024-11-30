from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)
