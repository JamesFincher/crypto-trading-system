from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class PerformanceLog(Base):
    __tablename__ = "performance_logs"

    id = Column(Integer, primary_key=True, index=True)
    trading_crew_id = Column(Integer, ForeignKey("trading_crews.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    metrics = Column(JSON)  # Store various performance metrics
    log_type = Column(String)  # e.g., "TRADE", "ERROR", "SYSTEM"
    message = Column(String)
    
    # Performance metrics
    pnl = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    
    # Relationships
    trading_crew = relationship("TradingCrew", back_populates="performance_logs")
