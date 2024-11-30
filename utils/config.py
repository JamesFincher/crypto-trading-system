"""
Configuration management for the crypto trading system.
Handles environment-specific settings and API configurations.
"""

import os
from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import validator, ConfigDict

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql://crypto_user:crypto_password@db:5432/crypto_trading"
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Binance API Configuration
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    BINANCE_TESTNET_API_KEY: Optional[str] = None
    BINANCE_TESTNET_SECRET_KEY: Optional[str] = None
    
    # PostgreSQL Configuration
    POSTGRES_USER: str = "crypto_user"
    POSTGRES_PASSWORD: str = "crypto_password"
    POSTGRES_DB: str = "crypto_trading"
    POSTGRES_HOST: str = "db"  # Use Docker service name
    POSTGRES_PORT: str = "5432"
    
    # Derived settings
    USE_TESTNET: bool = True
    
    @validator("USE_TESTNET", pre=True)
    def set_use_testnet(cls, v, values):
        """Determine if testnet should be used based on environment"""
        return values.get("ENVIRONMENT", "development").lower() == "development"
    
    @property
    def active_api_key(self) -> Optional[str]:
        """Get the appropriate API key based on environment"""
        return self.BINANCE_TESTNET_API_KEY if self.USE_TESTNET else self.BINANCE_API_KEY
    
    @property
    def active_api_secret(self) -> Optional[str]:
        """Get the appropriate API secret based on environment"""
        return self.BINANCE_TESTNET_SECRET_KEY if self.USE_TESTNET else self.BINANCE_API_SECRET

    @property
    def database_url(self) -> str:
        """Generate database URL from components or use override"""
        if "postgres" in self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = ConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    """
    Get cached settings instance.
    Returns:
        Settings: Application settings
    """
    return Settings()
