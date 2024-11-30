from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from schemas.data_sourcing import (
    DataFetchRequest,
    DataFetchResponse,
    DataPoint
)
from models.market_data import MarketData as MarketDataModel
from models.trading_crew import TradingCrew
from utils.binance_client import BinanceClientWrapper
from sqlalchemy import and_
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class DataSourcingService:
    """
    Service for fetching, storing, and managing market data from Binance.US.
    
    This service handles the interaction with the Binance API to fetch historical
    market data and stores it in the database. It provides functionality for
    retrieving stored data and managing data retention.
    
    Attributes:
        db (Session): SQLAlchemy database session
        binance_client (BinanceClientWrapper): Client for interacting with Binance.US API
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.binance_client = BinanceClientWrapper()

    def fetch_data(self, crew_id: int, start_time: int, end_time: int, intervals: List[str], user_id: int) -> Dict:
        """
        Fetch and store market data for a trading crew from Binance.US.
        
        This method performs the following operations:
        1. Validates the trading crew exists and belongs to the user
        2. Validates the requested time intervals
        3. Fetches historical klines data from Binance for each trading pair
        4. Stores the data in the database
        5. Returns the fetched data in a structured format
        
        Args:
            crew_id (int): ID of the trading crew
            start_time (int): Start timestamp in milliseconds
            end_time (int): End timestamp in milliseconds
            intervals (List[str]): List of time intervals (e.g., ["1h", "4h"])
            user_id (int): ID of the user making the request
            
        Returns:
            Dict: Nested dictionary containing fetched data organized by:
                {symbol: {interval: [data_points]}}
                where data_points contain OHLCV and additional market metrics
            
        Raises:
            HTTPException: 
                - 404: If trading crew not found
                - 400: If invalid intervals provided
                - 500: If Binance API error occurs
        """
        # Verify trading crew exists and belongs to user
        crew = self.db.query(TradingCrew).filter(
            TradingCrew.id == crew_id,
            TradingCrew.user_id == user_id
        ).first()
        if not crew:
            raise HTTPException(status_code=404, detail="Trading crew not found")

        # Validate intervals
        valid_intervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
        invalid_intervals = [interval for interval in intervals if interval not in valid_intervals]
        if invalid_intervals:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid intervals: {', '.join(invalid_intervals)}"
            )

        # Convert timestamps to datetime
        start_dt = datetime.fromtimestamp(start_time / 1000)
        end_dt = datetime.fromtimestamp(end_time / 1000)

        if end_dt <= start_dt:
            raise HTTPException(
                status_code=400,
                detail="Invalid time range: end time must be after start time"
            )

        result = {}
        
        # Fetch and store data for each trading pair and interval
        for symbol in crew.trading_pairs:
            result[symbol] = {}
            
            for interval in intervals:
                try:
                    # Fetch data from Binance
                    klines = self.binance_client.get_historical_klines(
                        symbol=symbol,
                        interval=interval,
                        start_time=start_dt,
                        end_time=end_dt
                    )
                    
                    # Process and store each kline
                    interval_data = []
                    for kline in klines:
                        # Convert Binance kline data to our format
                        timestamp = datetime.fromtimestamp(kline[0] / 1000)  # Open time
                        market_data = MarketDataModel(
                            crew_id=crew_id,
                            symbol=symbol,
                            interval=interval,
                            timestamp=timestamp,
                            open_price=float(kline[1]),
                            high_price=float(kline[2]),
                            low_price=float(kline[3]),
                            close_price=float(kline[4]),
                            volume=float(kline[5]),
                            additional_data={
                                "quote_volume": float(kline[7]),
                                "trades": int(kline[8]),
                                "taker_buy_base_volume": float(kline[9]),
                                "taker_buy_quote_volume": float(kline[10])
                            }
                        )
                        
                        # Store in database
                        self.db.add(market_data)
                        
                        # Add to result using DataPoint schema
                        data_point = DataPoint(
                            timestamp=timestamp,
                            open_price=float(kline[1]),
                            high_price=float(kline[2]),
                            low_price=float(kline[3]),
                            close_price=float(kline[4]),
                            volume=float(kline[5]),
                            additional_data={
                                "quote_volume": float(kline[7]),
                                "trades": int(kline[8]),
                                "taker_buy_base_volume": float(kline[9]),
                                "taker_buy_quote_volume": float(kline[10])
                            }
                        )
                        interval_data.append(data_point)
                    
                    result[symbol][interval] = interval_data
                    
                except BinanceAPIException as e:
                    logger.error(f"Binance API error for {symbol} with interval {interval}: {str(e)}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Binance API error for {symbol} with interval {interval}: {str(e)}"
                    )
                except ValueError as e:
                    logger.error(f"Value error for {symbol} with interval {interval}: {str(e)}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid data format for {symbol} with interval {interval}: {str(e)}"
                    )
                except Exception as e:
                    logger.error(f"Unexpected error for {symbol} with interval {interval}: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Internal server error while fetching data for {symbol} with interval {interval}"
                    )
        
        # Commit all changes to database
        self.db.commit()
        
        # Return response using DataFetchResponse schema
        return DataFetchResponse(
            crew_id=crew_id,
            status="success",
            data_points=result
        ).model_dump()

    def get_stored_data(
        self,
        crew_id: int,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[MarketDataModel]:
        """
        Retrieve stored market data from the database.
        
        This method queries the database for historical market data matching
        the specified criteria. It's useful for analysis, backtesting, and
        verifying stored data.
        
        Args:
            crew_id (int): ID of the trading crew
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            interval (str): Time interval (e.g., '1h', '4h')
            start_time (datetime): Start time for data retrieval
            end_time (datetime): End time for data retrieval
            
        Returns:
            List[MarketDataModel]: List of market data records matching the criteria
        """
        return self.db.query(MarketDataModel).filter(
            and_(
                MarketDataModel.crew_id == crew_id,
                MarketDataModel.symbol == symbol,
                MarketDataModel.interval == interval,
                MarketDataModel.timestamp >= start_time,
                MarketDataModel.timestamp <= end_time
            )
        ).order_by(MarketDataModel.timestamp.asc()).all()

    def clear_old_data(self, crew_id: int, before_date: datetime) -> int:
        """
        Remove historical market data older than the specified date.
        
        This method helps manage database size by removing old market data
        that is no longer needed for analysis or trading.
        
        Args:
            crew_id (int): ID of the trading crew
            before_date (datetime): Delete data older than this date
            
        Returns:
            int: Number of records deleted
        """
        result = self.db.query(MarketDataModel).filter(
            and_(
                MarketDataModel.crew_id == crew_id,
                MarketDataModel.timestamp < before_date
            )
        ).delete()
        self.db.commit()
        return result
