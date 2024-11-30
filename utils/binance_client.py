from binance.spot import Spot
from binance.error import ClientError
from typing import Dict, List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class BinanceClient:
    def __init__(self):
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.client = Spot(api_key=self.api_key, api_secret=self.api_secret)

    async def get_real_time_price(self, symbol: str) -> Dict:
        """Get real-time price for a symbol"""
        try:
            return await self.client.ticker_price(symbol)
        except ClientError as e:
            raise Exception(f"Failed to get price for {symbol}: {str(e)}")

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List:
        """Get historical klines/candlestick data"""
        try:
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            if start_time:
                params["startTime"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["endTime"] = int(end_time.timestamp() * 1000)
            
            return await self.client.klines(**params)
        except ClientError as e:
            raise Exception(f"Failed to get klines for {symbol}: {str(e)}")

    async def get_exchange_info(self, symbol: Optional[str] = None) -> Dict:
        """Get exchange information"""
        try:
            params = {}
            if symbol:
                params["symbol"] = symbol
            return await self.client.exchange_info(**params)
        except ClientError as e:
            raise Exception(f"Failed to get exchange info: {str(e)}")

    async def get_account_info(self) -> Dict:
        """Get account information"""
        try:
            return await self.client.account()
        except ClientError as e:
            raise Exception(f"Failed to get account info: {str(e)}")
