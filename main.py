from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

from database import engine, Base
from routers import (
    auth,
    binance_data,
    trading,
    paper_trading,
    data_sourcing,
    logs,
    management
)

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Automated Crypto Day Trading API",
    description="API for managing automated crypto trading operations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "testserver", "127.0.0.1"]
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(trading.router, prefix="/trading", tags=["Trading"])
app.include_router(paper_trading.router, prefix="/trading/paper", tags=["Paper Trading"])
app.include_router(data_sourcing.router, prefix="/data-sourcing", tags=["Data Sourcing"])
app.include_router(logs.router, prefix="/logs", tags=["Performance Logs"])
app.include_router(management.router, prefix="/management", tags=["Management"])
app.include_router(binance_data.router, prefix="/binance", tags=["Binance Data"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Automated Crypto Day Trading API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
