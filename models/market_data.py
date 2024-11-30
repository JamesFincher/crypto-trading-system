from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class MarketData(Base):
    """
    Market data model for storing historical price and volume data from Binance.
    
    This model stores OHLCV (Open, High, Low, Close, Volume) data along with additional
    market metrics for each trading pair and interval combination. Data is associated
    with a specific trading crew for strategy analysis and backtesting.
    
    Attributes:
        id (int): Primary key
        crew_id (int): Foreign key to trading_crews table
        symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
        interval (str): Time interval for the candlestick (e.g., '1h', '4h')
        timestamp (datetime): Opening time of the candlestick
        open_price (float): Opening price
        high_price (float): Highest price during the interval
        low_price (float): Lowest price during the interval
        close_price (float): Closing price
        volume (float): Trading volume
        created_at (datetime): Record creation timestamp
        additional_data (JSON): Additional market metrics including:
            - quote_volume: Volume in quote currency
            - trades: Number of trades
            - taker_buy_base_volume: Volume of base asset bought by takers
            - taker_buy_quote_volume: Volume of quote asset bought by takers
    """
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer, ForeignKey("trading_crews.id"), nullable=False)
    symbol = Column(String, nullable=False)
    interval = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    additional_data = Column(JSON, nullable=True)

    # Relationship with TradingCrew
    trading_crew = relationship("TradingCrew", back_populates="market_data")

    class Config:
        orm_mode = True
