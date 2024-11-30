from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class MarketData(Base):
    """
    Market data model for storing historical price and volume data.
    """
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer, ForeignKey("trading_crews.id"), nullable=False)
    symbol = Column(String, nullable=False)
    interval = Column(String, nullable=False)  # e.g., "1h", "4h"
    timestamp = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    additional_data = Column(JSON, nullable=True)  # For storing indicators or other metadata

    # Relationship with TradingCrew
    trading_crew = relationship("TradingCrew", back_populates="market_data")

    class Config:
        orm_mode = True
