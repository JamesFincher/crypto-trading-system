from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from services.paper_trading_service import PaperTradingService
from schemas.paper_trading import (
    PaperTradingSessionCreate,
    PaperTradingSessionResponse,
    PaperTradeCreate,
    PaperTradeResponse,
    PerformanceMetrics
)

router = APIRouter(prefix="/paper-trading", tags=["Paper Trading"])

@router.post("/sessions", response_model=PaperTradingSessionResponse, status_code=201)
async def create_session(
    session: PaperTradingSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new paper trading session"""
    try:
        return PaperTradingService.create_session(db, session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions", response_model=List[PaperTradingSessionResponse])
async def get_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all paper trading sessions"""
    return PaperTradingService.get_sessions(db, skip=skip, limit=limit)

@router.get("/sessions/{session_id}", response_model=PaperTradingSessionResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific paper trading session"""
    session = PaperTradingService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/sessions/{session_id}/trades", response_model=PaperTradeResponse)
async def create_trade(
    session_id: int,
    trade: PaperTradeCreate,
    db: Session = Depends(get_db)
):
    """Create a new paper trade in a session"""
    try:
        if trade.session_id != session_id:
            raise HTTPException(status_code=400, detail="Session ID mismatch")
        return PaperTradingService.create_trade(db, trade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/sessions/{session_id}/trades/{trade_id}/close", response_model=PaperTradeResponse)
async def close_trade(
    session_id: int,
    trade_id: int,
    exit_price: float = Query(..., gt=0),
    db: Session = Depends(get_db)
):
    """Close a paper trade"""
    trade = PaperTradingService.close_trade(db, trade_id, exit_price)
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found or already closed")
    if trade.session_id != session_id:
        raise HTTPException(status_code=400, detail="Trade does not belong to this session")
    return trade

@router.get("/sessions/{session_id}/trades", response_model=List[PaperTradeResponse])
async def get_session_trades(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get all trades for a specific session"""
    session = PaperTradingService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.trades

@router.get("/sessions/{session_id}/metrics", response_model=PerformanceMetrics)
async def get_session_metrics(
    session_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get performance metrics for a session"""
    session = PaperTradingService.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update unrealized PnL for open trades
    PaperTradingService.update_unrealized_pnl(db, session_id)
    
    return PaperTradingService.calculate_performance_metrics(
        db,
        session_id,
        start_date=start_date,
        end_date=end_date
    )
