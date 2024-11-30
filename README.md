# Crypto Trading System

A robust API for managing automated crypto trading operations with Binance integration.

## Features

- User Authentication and Authorization
- Real-time Binance Data Integration
  - Historical market data fetching with customizable intervals
  - OHLCV (Open, High, Low, Close, Volume) data storage
  - Additional market metrics (quote volumes, trade counts)
  - Automatic data persistence for analysis
- Paper Trading Support
- Performance Logging
- Trading Crew Management
- Data Sourcing and Analysis

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Poetry for dependency management
- SQLite (default) or PostgreSQL
- Binance API credentials (for live trading)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crypto-trading-system.git
cd crypto-trading-system
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up environment variables:
```bash
cp example.env .env
```
Edit `.env` with your configuration values.

### Environment Variables

Required environment variables:

```bash
# Database
DATABASE_URL=sqlite:///./crypto_trading.db

# Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Binance API (Required for market data)
BINANCE_API_KEY=your-binance-us-api-key
BINANCE_API_SECRET=your-binance-us-api-secret
```

Note: This system uses the Binance.US API endpoint. Make sure to obtain API credentials from Binance.US if you're in the United States.

### Database Setup

1. Initialize the database:
```bash
poetry run alembic upgrade head
```

This will create all necessary database tables.

For future database changes:
```bash
# After modifying SQLAlchemy models, generate a new migration
poetry run alembic revision --autogenerate -m "Description of changes"

# Apply the migration
poetry run alembic upgrade head
```

### Running the Application

1. Start the server:
```bash
poetry run uvicorn main:app --reload
```

2. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

- `POST /auth/login` - Login and get access token
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```

### Trading Operations

- `GET /trading/crews` - List all trading crews
- `POST /trading/crews` - Create a new trading crew
- `GET /trading/paper` - Get paper trading status
- `POST /trading/paper/start` - Start paper trading

### Data Management

- `GET /data/source` - Get available data sources
- `POST /data/source` - Add a new data source
- `GET /logs` - Get trading logs
- `POST /logs` - Create a new log entry

### Market Data

The system fetches and stores market data with the following features:

- Customizable time intervals (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d)
- Historical data retrieval with specified date ranges
- Automatic data persistence for each trading crew
- Comprehensive market metrics including:
  - OHLCV (Open, High, Low, Close, Volume)
  - Quote asset volume
  - Number of trades
  - Taker buy volumes (base and quote)

Example API usage:

```python
# Fetch market data for a trading crew
response = client.post("/data-sourcing/fetch", json={
    "crew_id": 1,
    "start_time": 1625097600000,  # Unix timestamp in milliseconds
    "end_time": 1625184000000,
    "intervals": ["1h", "4h"]
})
```

## Testing

Run the test suite:
```bash
poetry run pytest
```

For test coverage:
```bash
poetry run pytest --cov
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
