from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id = Column(Integer, primary_key=True, index=True)
    trading_crew_id = Column(Integer, ForeignKey("trading_crews.id"))
    symbol = Column(String)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float)
    side = Column(String)  # "BUY" or "SELL"
    status = Column(String)  # "OPEN" or "CLOSED"
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    pnl = Column(Float, nullable=True)
    
    # Relationships
    trading_crew = relationship("TradingCrew", back_populates="paper_trades")
