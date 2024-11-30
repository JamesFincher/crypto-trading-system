# Crypto Trading System

A robust API for managing automated crypto trading operations with Binance integration.

## Features

- User Authentication and Authorization
- Real-time Binance Data Integration
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
