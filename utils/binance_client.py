"""
Binance API client utility for interacting with the Binance cryptocurrency exchange.

This module provides a client class that wraps the Binance API endpoints for retrieving
market data, including real-time prices, historical data, order book information,
and various other market statistics.
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException
import os
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import logging
from .config import get_settings

logger = logging.getLogger(__name__)

class BinanceClientWrapper:
    """Wrapper for Binance Client with support for both mainnet and testnet"""
    
    # API URLs
    MAINNET_API_URL = "https://api.binance.us"
    MAINNET_STREAM_URL = "wss://stream.binance.us:9443"
    
    # Testnet base URLs
    TESTNET_API_URL = "https://testnet.binance.vision/api"
    TESTNET_STREAM_URL = "wss://stream.testnet.binance.vision"
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, testnet: Optional[bool] = None):
        """
        Initialize Binance client with optional testnet support.
        In development environment (ENVIRONMENT=development), testnet is used by default.
        
        Args:
            api_key: Binance API key (optional, will use from config if not provided)
            api_secret: Binance API secret (optional, will use from config if not provided)
            testnet: Whether to use testnet (optional, will determine from config if not provided)
        """
        settings = get_settings()
        
        # Determine if we should use testnet
        self.testnet = testnet if testnet is not None else settings.USE_TESTNET
        
        if self.testnet:
            logger.info("Using Binance testnet environment")
            self.api_key = api_key or settings.BINANCE_TESTNET_API_KEY
            self.api_secret = api_secret or settings.BINANCE_TESTNET_SECRET_KEY
            self.base_url = self.TESTNET_API_URL
            self.stream_url = self.TESTNET_STREAM_URL
        else:
            logger.info("Using Binance.US mainnet environment")
            self.api_key = api_key or settings.BINANCE_API_KEY
            self.api_secret = api_secret or settings.BINANCE_API_SECRET
            self.base_url = self.MAINNET_API_URL
            self.stream_url = self.MAINNET_STREAM_URL
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                f"{'Testnet' if self.testnet else 'Mainnet'} API credentials not found. "
                "Please check your environment variables."
            )
        
        # Initialize the Binance client
        self.client = Client(
            api_key=self.api_key,
            api_secret=self.api_secret,
            testnet=self.testnet,
            tld='us' if not self.testnet else None
        )
        
        # Set appropriate API URL
        if self.testnet:
            self.client.API_URL = self.TESTNET_API_URL
            logger.info("Initialized Binance client in testnet mode")
        else:
            self.client.API_URL = self.MAINNET_API_URL
            logger.info("Initialized Binance.US client in mainnet mode")
            
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
            return self.client.get_symbol_ticker(symbol=symbol)
        except BinanceAPIException as e:
            logger.error(f"Error fetching real-time price: {str(e)}")
            raise
            
    def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 500
    ) -> list:
        """
        Get historical klines/candlestick data
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            interval: Kline interval (e.g. '1m', '5m', '1h', '1d')
            start_time: Start time for historical data
            end_time: End time for historical data  
            limit: Number of klines to return (max 1000)
        
        Returns:
            List of kline data
        """
        try:
            # Convert datetime to millisecond timestamps if provided
            start_str = int(start_time.timestamp() * 1000) if start_time else None
            end_str = int(end_time.timestamp() * 1000) if end_time else None
            
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_str,
                end_str=end_str,
                limit=limit
            )
            return klines
            
        except BinanceAPIException as e:
            logger.error(f"Error fetching historical klines: {str(e)}")
            raise
            
    def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange information including trading rules and symbol information"""
        try:
            return self.client.get_exchange_info()
        except BinanceAPIException as e:
            logger.error(f"Error fetching exchange info: {str(e)}")
            raise
            
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get symbol specific trading rules and information"""
        try:
            exchange_info = self.get_exchange_info()
            for sym_info in exchange_info['symbols']:
                if sym_info['symbol'] == symbol:
                    return sym_info
            raise ValueError(f"Symbol {symbol} not found")
        except BinanceAPIException as e:
            logger.error(f"Error fetching symbol info: {str(e)}")
            raise
            
    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: Optional[str] = 'GTC',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new order
        
        Args:
            symbol: Trading pair symbol
            side: Order side (BUY or SELL)
            order_type: Order type (LIMIT, MARKET, etc)
            quantity: Order quantity
            price: Order price (required for limit orders)
            time_in_force: Time in force (GTC, IOC, FOK)
            **kwargs: Additional order parameters
            
        Returns:
            Order response from Binance API
        """
        try:
            # Get symbol info for precision requirements
            symbol_info = self.get_symbol_info(symbol)
            price_filter = next(filter(lambda x: x['filterType'] == 'PRICE_FILTER', symbol_info['filters']))
            tick_size = float(price_filter['tickSize'])
            
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity,
                **kwargs
            }
            
            if order_type == 'LIMIT':
                if not price:
                    raise ValueError("Price is required for LIMIT orders")
                # Round price to the correct precision
                decimal_places = len(str(tick_size).split('.')[-1].rstrip('0'))
                params['price'] = round(float(price), decimal_places)
                params['timeInForce'] = time_in_force
                
            return self.client.create_order(**params)
            
        except BinanceAPIException as e:
            logger.error(f"Error creating order: {str(e)}")
            raise
            
    def get_account_info(self) -> Dict[str, Any]:
        """Get current account information"""
        try:
            return self.client.get_account()
        except BinanceAPIException as e:
            logger.error(f"Error fetching account info: {str(e)}")
            raise
            
    def get_asset_balance(self, asset: str) -> Dict[str, str]:
        """
        Get current balance of a specific asset
        
        Args:
            asset: Asset symbol (e.g. 'BTC', 'USDT')
            
        Returns:
            Dict containing free and locked amounts
        """
        try:
            return self.client.get_asset_balance(asset=asset)
        except BinanceAPIException as e:
            logger.error(f"Error fetching {asset} balance: {str(e)}")
            raise
            
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
            data = self.client.get_order_book(symbol=symbol, limit=limit)
            
            # Transform bids and asks into the required format
            transformed_data = {
                "symbol": symbol,
                "timestamp": datetime.now(),  # Binance doesn't provide timestamp in depth endpoint
                "bids": [{"price": float(bid[0]), "quantity": float(bid[1])} for bid in data["bids"]],
                "asks": [{"price": float(ask[0]), "quantity": float(ask[1])} for ask in data["asks"]],
                "last_update_id": data["lastUpdateId"]
            }
            return transformed_data
        except BinanceAPIException as e:
            logger.error(f"Error fetching orderbook: {str(e)}")
            raise
            
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
            data = self.client.get_recent_trades(symbol=symbol, limit=limit)
            return [self._transform_trade(trade) for trade in data]
        except BinanceAPIException as e:
            logger.error(f"Error fetching recent trades: {str(e)}")
            raise
            
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

            trades = self.client.get_aggregate_trades(**params)
            return [self._transform_agg_trade(trade) for trade in trades]
        except BinanceAPIException as e:
            logger.error(f"Error fetching aggregated trades: {str(e)}")
            raise
            
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
            data = self.client.get_ticker_24hr(symbol=symbol)
            
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
        except BinanceAPIException as e:
            logger.error(f"Error fetching 24hr ticker data: {str(e)}")
            raise
            
    def get_ticker_book(self, symbol: str) -> Dict:
        """
        Get best price/quantity on the order book.
        
        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dict: Best price/quantity on the order book
        """
        try:
            data = self.client.get_ticker_book(symbol=symbol)
            
            # Transform response to match our model
            return {
                "symbol": data["symbol"],
                "bid_price": data["bidPrice"],
                "bid_quantity": data["bidQty"],
                "ask_price": data["askPrice"],
                "ask_quantity": data["askQty"]
            }
        except BinanceAPIException as e:
            logger.error(f"Error fetching book ticker: {str(e)}")
            raise
            
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
            return self.client.get_ticker_price(symbol=symbol) if symbol else self.client.get_all_tickers()
        except BinanceAPIException as e:
            logger.error(f"Error fetching ticker price: {str(e)}")
            raise
            
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
            return self.client.get_historical_trades(**params)
        except BinanceAPIException as e:
            logger.error(f"Error fetching historical trades: {str(e)}")
            raise
