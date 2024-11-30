# Automated Crypto Day Trading System

A robust FastAPI-based system for automated cryptocurrency trading using Binance integration.

## Features

- Real-time and historical market data from Binance
- Paper trading support for strategy testing
- Live trading operations
- Performance logging and analytics
- Trading crew management
- Data sourcing and preprocessing
- Authentication and authorization

## Requirements

- Python 3.9+
- Poetry for dependency management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JamesFincher/crypto-trading-system.git
cd crypto-trading-system
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Create a `.env` file with your configuration:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Development

1. Activate the Poetry virtual environment:
```bash
poetry shell
```

2. Run the development server:
```bash
poetry run uvicorn main:app --reload
```

3. Run tests:
```bash
poetry run pytest
```

4. Format code:
```bash
poetry run black .
poetry run isort .
```

5. Check code quality:
```bash
poetry run flake8
poetry run mypy .
```

## Docker

Build and run using Docker:

```bash
docker-compose up --build
```

## API Documentation

Once running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT License
