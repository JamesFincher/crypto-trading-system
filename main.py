from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
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
    title="Crypto Trading System",
    description="A FastAPI-based cryptocurrency trading system with paper trading capabilities",
    version="1.0.0",
    docs_url=None,  # Disable the default docs
    redoc_url=None  # Disable the default redoc
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
app.include_router(binance_data.router)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Crypto Trading System API",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        init_oauth={
            "usePkceWithAuthorizationCodeGrant": True,
            "clientId": "crypto-trading-system",
        }
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title="Crypto Trading System API",
        version="1.0.0",
        description="A FastAPI-based cryptocurrency trading system with paper trading capabilities",
        routes=app.routes,
        servers=[{"url": "http://localhost:8000"}],
        components={
            "securitySchemes": {
                "OAuth2PasswordBearer": {
                    "type": "oauth2",
                    "flows": {
                        "password": {
                            "tokenUrl": "/auth/login",
                            "scopes": {}
                        }
                    }
                }
            }
        },
        security=[{"OAuth2PasswordBearer": []}]
    )

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Crypto Trading System API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
