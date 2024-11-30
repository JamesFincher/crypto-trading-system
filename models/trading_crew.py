from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TradingCrew(Base):
    __tablename__ = "trading_crews"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    strategy_config = Column(JSON)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Trading parameters
    max_position_size = Column(Float)
    risk_percentage = Column(Float)
    trading_pairs = Column(JSON)  # List of trading pairs
    
    # Relationships
    user = relationship("User", back_populates="trading_crews")
    paper_trades = relationship("PaperTrade", back_populates="trading_crew")
    performance_logs = relationship("PerformanceLog", back_populates="trading_crew")
    market_data = relationship("MarketData", back_populates="trading_crew", cascade="all, delete-orphan")
