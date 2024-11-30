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
from utils.binance_client import BinanceClient
from sqlalchemy import and_
from fastapi import HTTPException

class DataSourcingService:
    def __init__(self, db: Session):
        self.db = db
        self.binance_client = BinanceClient()

    async def fetch_data(self, crew_id: int, start_time: int, end_time: int, intervals: List[str]) -> Dict:
        """
        Fetch and store market data for a trading crew
        
        Args:
            crew_id: ID of the trading crew
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
            intervals: List of time intervals (e.g., ["1h", "4h"])
            
        Returns:
            Dict containing fetched data for each interval
        """
        # Verify trading crew exists
        crew = self.db.query(TradingCrew).filter(TradingCrew.id == crew_id).first()
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
                detail="End time must be after start time"
            )

        result = {}
        
        # Fetch and store data for each trading pair and interval
        for symbol in crew.trading_pairs:
            result[symbol] = {}
            
            for interval in intervals:
                try:
                    # Fetch data from Binance
                    klines = await self.binance_client.get_klines(
                        symbol=symbol,
                        interval=interval,
                        start_time=start_dt,
                        end_time=end_dt
                    )
                    
                    # Process and store each kline
                    interval_data = []
                    for kline in klines:
                        # Convert Binance kline data to our format
                        market_data = MarketDataModel(
                            crew_id=crew_id,
                            symbol=symbol,
                            interval=interval,
                            timestamp=datetime.fromtimestamp(kline[0] / 1000),  # Open time
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
                        
                        # Add to result
                        interval_data.append({
                            "timestamp": market_data.timestamp.isoformat(),
                            "open": market_data.open_price,
                            "high": market_data.high_price,
                            "low": market_data.low_price,
                            "close": market_data.close_price,
                            "volume": market_data.volume
                        })
                    
                    result[symbol][interval] = interval_data
                
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to fetch data for {symbol} with interval {interval}: {str(e)}"
                    )
        
        # Commit all changes to database
        self.db.commit()
        
        return {
            "crew_id": crew_id,
            "status": "success",
            "data_points": result
        }

    async def get_stored_data(
        self,
        crew_id: int,
        symbol: str,
        interval: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[MarketDataModel]:
        """Retrieve stored market data for a trading crew"""
        return self.db.query(MarketDataModel).filter(
            and_(
                MarketDataModel.crew_id == crew_id,
                MarketDataModel.symbol == symbol,
                MarketDataModel.interval == interval,
                MarketDataModel.timestamp >= start_time,
                MarketDataModel.timestamp <= end_time
            )
        ).order_by(MarketDataModel.timestamp.asc()).all()

    async def clear_old_data(self, crew_id: int, before_date: datetime) -> int:
        """Clear historical data older than specified date"""
        result = self.db.query(MarketDataModel).filter(
            and_(
                MarketDataModel.crew_id == crew_id,
                MarketDataModel.timestamp < before_date
            )
        ).delete()
        self.db.commit()
        return result
