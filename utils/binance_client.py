"""
Binance API client utility for interacting with the Binance cryptocurrency exchange.

This module provides a client class that wraps the Binance API endpoints for retrieving
market data, including real-time prices, historical data, order book information,
and various other market statistics.
"""

from binance.spot import Spot
from binance.error import ClientError
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class BinanceClient:
    """
    A client for interacting with the Binance API.

    This class provides methods to access various Binance API endpoints for market data
    and trading information. It handles authentication and request formatting.

    Attributes:
        api_key (str): Binance API key loaded from environment variables
        api_secret (str): Binance API secret loaded from environment variables
        client (Spot): Binance Spot API client
    """

    def __init__(self):
        """Initialize the Binance client with API credentials from environment variables."""
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        # Use Binance.US API endpoint
        self.client = Spot(
            api_key=self.api_key,
            api_secret=self.api_secret,
            base_url="https://api.binance.us"
        )

    def get_real_time_price(self, symbol: str) -> Dict:
        """
        Get real-time price for a symbol.

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            Dict: Real-time price data for the symbol

        Raises:
            Exception: If the API request fails
        """
        try:
            return self.client.ticker_price(symbol)
        except ClientError as e:
            if e.status_code == 451:
                raise Exception("Access restricted. Please ensure you're using Binance.US API keys and accessing from a supported region.")
            raise Exception(f"Failed to get price for {symbol}: {str(e)}")

    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List:
        """
        Get historical klines/candlestick data.

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            interval (str): Kline interval (e.g., '1m', '5m', '1h')
            start_time (Optional[datetime]): Start time for the klines (default: None)
            end_time (Optional[datetime]): End time for the klines (default: None)
            limit (int): Number of klines to retrieve (default: 1000, max: 1000)

        Returns:
            List: List of kline data

        Raises:
            Exception: If the API request fails
        """
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
            
            klines = self.client.klines(**params)
            
            # Transform klines to match our model
            transformed_klines = []
            for kline in klines:
                transformed_klines.append({
                    "open_time": datetime.fromtimestamp(kline[0] / 1000),
                    "open": float(kline[1]),
                    "high": float(kline[2]),
                    "low": float(kline[3]),
                    "close": float(kline[4]),
                    "volume": float(kline[5]),
                    "close_time": datetime.fromtimestamp(kline[6] / 1000),
                    "quote_volume": float(kline[7]),
                    "trades": int(kline[8])
                })
            
            return transformed_klines
        except ClientError as e:
            if e.status_code == 451:
                raise Exception("Access restricted. Please ensure you're using Binance.US API keys and accessing from a supported region.")
            raise Exception(f"Failed to get klines for {symbol}: {str(e)}")

    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict:
        """
        Get exchange information.

        Args:
            symbol (Optional[str]): Trading pair symbol (e.g., 'BTCUSDT')
                                If None, returns data for all symbols

        Returns:
            Dict: Exchange information including trading rules and symbol details

        Raises:
            Exception: If the API request fails
        """
        try:
            params = {}
            if symbol:
                params["symbol"] = symbol
            
            data = self.client.exchange_info(**params)
            
            # Transform to match our model
            return {
                "timezone": data["timezone"],
                "server_time": datetime.fromtimestamp(data["serverTime"] / 1000),
                "rate_limits": data["rateLimits"],
                "symbols": data["symbols"]
            }
        except ClientError as e:
            if e.status_code == 451:
                raise Exception("Access restricted. Please ensure you're using Binance.US API keys and accessing from a supported region.")
            raise Exception(f"Failed to get exchange info: {str(e)}")

    def get_account_info(self) -> Dict:
        """
        Get account information including balances.

        Returns:
            Dict: Account information including balances

        Raises:
            Exception: If the API request fails
        """
        try:
            return self.client.account()
        except ClientError as e:
            if e.status_code == 451:
                raise Exception("Access restricted. Please ensure you're using Binance.US API keys and accessing from a supported region.")
            raise Exception(f"Failed to get account info: {str(e)}")

    def get_orderbook(self, symbol: str, limit: Optional[int] = 100) -> Dict:
        """
        Get order book for a symbol.

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            limit (Optional[int]): Number of bids/asks to retrieve (default: 100)

        Returns:
            Dict: Order book data containing bids and asks

        Raises:
            Exception: If the API request fails
        """
        try:
            data = self.client.depth(symbol, limit=limit)
            
            # Transform bids and asks into the required format
            transformed_data = {
                "symbol": symbol,
                "timestamp": datetime.now(),  # Binance doesn't provide timestamp in depth endpoint
                "bids": [{"price": float(bid[0]), "quantity": float(bid[1])} for bid in data["bids"]],
                "asks": [{"price": float(ask[0]), "quantity": float(ask[1])} for ask in data["asks"]],
                "last_update_id": data["lastUpdateId"]
            }
            return transformed_data
        except ClientError as e:
            if e.status_code == 451:
                raise Exception("Access restricted. Please ensure you're using Binance.US API keys and accessing from a supported region.")
            raise Exception(f"Failed to get orderbook for {symbol}: {str(e)}")

    def get_recent_trades(self, symbol: str, limit: Optional[int] = 500) -> List:
        """
        Get recent trades for a symbol.

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            limit (Optional[int]): Number of trades to retrieve (default: 500, max: 1000)

        Returns:
            List: List of recent trades

        Raises:
            Exception: If the API request fails
        """
        try:
            data = self.client.trades(symbol, limit=limit)
            return [self._transform_trade(trade) for trade in data]
        except ClientError as e:
            if e.status_code == 451:
                raise Exception("Access restricted. Please ensure you're using Binance.US API keys and accessing from a supported region.")
            raise Exception(f"Failed to get recent trades for {symbol}: {str(e)}")

    def _transform_trade(self, data: Dict) -> Dict:
        """Transform trade data to match our model."""
        return {
            "id": data["id"],
            "price": float(data["price"]),
            "quantity": float(data["qty"]),
            "time": datetime.fromtimestamp(data["time"] / 1000),
            "is_buyer_maker": data["isBuyerMaker"],
            "is_best_match": data["isBestMatch"]
        }

    def get_aggregated_trades(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = 500
    ) -> List:
        """
        Get compressed/aggregate trades for a symbol.

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            start_time (Optional[datetime]): Start time for the trades (default: None)
            end_time (Optional[datetime]): End time for the trades (default: None)
            limit (Optional[int]): Number of trades to retrieve (default: 500, max: 1000)

        Returns:
            List: List of aggregated trades

        Raises:
            Exception: If the API request fails
        """
        try:
            params = {
                "symbol": symbol,
                "limit": limit
            }
            if start_time:
                params["startTime"] = int(start_time.timestamp() * 1000)
            if end_time:
                params["endTime"] = int(end_time.timestamp() * 1000)

            trades = self.client.agg_trades(**params)
            return [self._transform_agg_trade(trade) for trade in trades]
        except ClientError as e:
            if e.status_code == 451:
                raise Exception("Access restricted. Please ensure you're using Binance.US API keys and accessing from a supported region.")
            raise Exception(f"Failed to get aggregated trades for {symbol}: {str(e)}")

    def _transform_agg_trade(self, data: Dict) -> Dict:
        """Transform aggregate trade data to match our model."""
        return {
            "id": data["a"],  # Aggregate trade ID
            "price": float(data["p"]),  # Price
            "quantity": float(data["q"]),  # Quantity
            "first_trade_id": data["f"],  # First trade ID
            "last_trade_id": data["l"],  # Last trade ID
            "time": datetime.fromtimestamp(data["T"] / 1000),  # Timestamp
            "is_buyer_maker": data["m"],  # Is buyer maker
            "is_best_match": data["M"]  # Best price match
        }

    def get_ticker_24hr(self, symbol: str) -> Dict:
        """
        Get 24-hour ticker price change statistics.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dict: 24-hour ticker statistics
        """
        try:
            data = self.client.ticker_24hr(symbol)
            
            # Transform response to match our model
            return {
                "symbol": data["symbol"],
                "price_change": data["priceChange"],
                "price_change_percent": data["priceChangePercent"],
                "weighted_avg_price": data["weightedAvgPrice"],
                "prev_close_price": data["prevClosePrice"],
                "last_price": data["lastPrice"],
                "bid_price": data["bidPrice"],
                "ask_price": data["askPrice"],
                "open_price": data["openPrice"],
                "high_price": data["highPrice"],
                "low_price": data["lowPrice"],
                "volume": data["volume"],
                "quote_volume": data["quoteVolume"],
                "open_time": datetime.fromtimestamp(data["openTime"] / 1000),
                "close_time": datetime.fromtimestamp(data["closeTime"] / 1000),
                "first_trade_id": data["firstId"],
                "last_trade_id": data["lastId"],
                "trade_count": data["count"]
            }
        except ClientError as e:
            if e.status_code == 451:
                raise Exception("Access restricted. Please ensure you're using Binance.US API keys and accessing from a supported region.")
            raise Exception(f"Failed to get 24hr ticker data: {str(e)}")

    def get_ticker_book(self, symbol: str) -> Dict:
        """
        Get best price/quantity on the order book.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dict: Best price/quantity on the order book
        """
        try:
            data = self.client.book_ticker(symbol)
            
            # Transform response to match our model
            return {
                "symbol": data["symbol"],
                "bid_price": data["bidPrice"],
                "bid_quantity": data["bidQty"],
                "ask_price": data["askPrice"],
                "ask_quantity": data["askQty"]
            }
        except ClientError as e:
            if e.status_code == 451:
                raise Exception("Access restricted. Please ensure you're using Binance.US API keys and accessing from a supported region.")
            raise Exception(f"Failed to get book ticker: {str(e)}")

    def get_ticker_price(self, symbol: Optional[str] = None) -> Union[Dict, List[Dict]]:
        """
        Get latest price for a symbol or all symbols.

        Args:
            symbol (Optional[str]): Trading pair symbol (e.g., 'BTCUSDT')
                                If None, returns data for all symbols

        Returns:
            Union[Dict, List[Dict]]: Latest price data for one or all symbols

        Raises:
            Exception: If the API request fails
        """
        try:
            return self.client.ticker_price(symbol) if symbol else self.client.ticker_price()
        except ClientError as e:
            if e.status_code == 451:
                raise Exception("Access restricted. Please ensure you're using Binance.US API keys and accessing from a supported region.")
            raise Exception(f"Failed to get ticker price: {str(e)}")

    def get_historical_trades(
        self,
        symbol: str,
        limit: Optional[int] = 500,
        from_id: Optional[int] = None
    ) -> List:
        """
        Get historical trades (requires API key).

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            limit (Optional[int]): Number of trades to retrieve (default: 500, max: 1000)
            from_id (Optional[int]): Trade ID to start from (default: None)

        Returns:
            List: List of historical trades

        Raises:
            Exception: If the API request fails
        """
        try:
            params = {"symbol": symbol, "limit": limit}
            if from_id:
                params["fromId"] = from_id
            return self.client.historical_trades(**params)
        except ClientError as e:
            if e.status_code == 451:
                raise Exception("Access restricted. Please ensure you're using Binance.US API keys and accessing from a supported region.")
            raise Exception(f"Failed to get historical trades for {symbol}: {str(e)}")
