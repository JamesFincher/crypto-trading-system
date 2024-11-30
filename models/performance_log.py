from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class PerformanceLog(Base):
    __tablename__ = "performance_logs"

    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer, ForeignKey("trading_crews.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    profit = Column(Float)
    message = Column(String)
    
    # Relationships
    trading_crew = relationship("TradingCrew", back_populates="performance_logs")
