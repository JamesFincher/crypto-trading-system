from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from schemas.paper_trading import TradeStatus, TradeSide

class PaperTradingSession(Base):
    __tablename__ = "paper_trading_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    strategy_config = Column(JSON)  # Stores strategy type and parameters
    trading_pairs = Column(JSON)  # Stores list of trading pairs
    risk_percentage = Column(Float)
    initial_balance = Column(Float)
    current_balance = Column(Float)
    max_position_size = Column(Float)
    total_pnl = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    trades = relationship("PaperTrade", back_populates="session", cascade="all, delete-orphan")

class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("paper_trading_sessions.id"))
    crew_id = Column(Integer, ForeignKey("trading_crews.id"))  
    symbol = Column(String)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float)
    side = Column(SQLEnum(TradeSide))
    status = Column(SQLEnum(TradeStatus), default=TradeStatus.OPEN)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    realized_pnl = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, nullable=True)
    roi_percentage = Column(Float, nullable=True)
    
    # Relationships
    session = relationship("PaperTradingSession", back_populates="trades")
    trading_crew = relationship("TradingCrew", back_populates="paper_trades")  
