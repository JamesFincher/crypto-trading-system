from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import numpy as np

from models.paper_trade import PaperTrade, PaperTradingSession
from schemas.paper_trading import (
    PaperTradeCreate,
    PaperTradingSessionCreate,
    PerformanceMetrics,
    TradeStatus,
    TradeSide
)
from utils.binance_client import BinanceClientWrapper

class PaperTradingService:
    @staticmethod
    def create_session(db: Session, session_data: PaperTradingSessionCreate) -> PaperTradingSession:
        """Create a new paper trading session"""
        session = PaperTradingSession(
            name=session_data.name,
            strategy_config=session_data.strategy_config.dict(),
            trading_pairs=session_data.trading_pairs,
            risk_percentage=session_data.risk_percentage,
            initial_balance=session_data.initial_balance,
            current_balance=session_data.initial_balance,
            max_position_size=session_data.max_position_size
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: Session, session_id: int) -> Optional[PaperTradingSession]:
        """Get a specific paper trading session"""
        return db.query(PaperTradingSession).filter(PaperTradingSession.id == session_id).first()

    @staticmethod
    def get_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[PaperTradingSession]:
        """Get all paper trading sessions"""
        return db.query(PaperTradingSession).offset(skip).limit(limit).all()

    @staticmethod
    def create_trade(db: Session, trade: PaperTradeCreate) -> PaperTrade:
        """Create a new paper trade"""
        # Get the session
        session = PaperTradingService.get_session(db, trade.session_id)
        if not session:
            raise ValueError("Session not found")

        # Validate trading pair
        if trade.symbol not in session.trading_pairs:
            raise ValueError(f"Trading pair {trade.symbol} not allowed in this session")

        # Calculate trade value
        trade_value = trade.entry_price * trade.quantity

        # Check if trade value exceeds max position size
        if trade_value > session.max_position_size:
            raise ValueError(f"Trade value {trade_value} exceeds max position size {session.max_position_size}")

        # Check if we have enough balance
        if trade.side == TradeSide.BUY and trade_value > session.current_balance:
            raise ValueError(f"Insufficient balance for trade")

        # Create the trade
        db_trade = PaperTrade(
            session_id=trade.session_id,
            symbol=trade.symbol,
            entry_price=trade.entry_price,
            quantity=trade.quantity,
            side=trade.side,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,
            status=TradeStatus.OPEN
        )
        db.add(db_trade)

        # Update session balance
        if trade.side == TradeSide.BUY:
            session.current_balance -= trade_value
        
        db.commit()
        db.refresh(db_trade)
        return db_trade

    @staticmethod
    def close_trade(db: Session, trade_id: int, exit_price: float) -> Optional[PaperTrade]:
        """Close a paper trade"""
        trade = db.query(PaperTrade).filter(PaperTrade.id == trade_id).first()
        if not trade or trade.status != TradeStatus.OPEN:
            return None

        trade.exit_price = exit_price
        trade.exit_time = datetime.utcnow()
        trade.status = TradeStatus.CLOSED

        # Calculate PnL
        trade_value = trade.quantity * trade.exit_price
        entry_value = trade.quantity * trade.entry_price
        
        if trade.side == TradeSide.BUY:
            trade.realized_pnl = trade_value - entry_value
            trade.roi_percentage = ((trade_value - entry_value) / entry_value) * 100
        else:  # SELL
            trade.realized_pnl = entry_value - trade_value
            trade.roi_percentage = ((entry_value - trade_value) / entry_value) * 100

        # Update session
        session = trade.session
        session.current_balance += trade_value if trade.side == TradeSide.BUY else entry_value
        session.total_pnl += trade.realized_pnl

        db.commit()
        db.refresh(trade)
        return trade

    @staticmethod
    def update_unrealized_pnl(db: Session, session_id: int) -> None:
        """Update unrealized PnL for all open trades in a session"""
        binance_client = BinanceClientWrapper()
        open_trades = (
            db.query(PaperTrade)
            .filter(
                PaperTrade.session_id == session_id,
                PaperTrade.status == TradeStatus.OPEN
            )
            .all()
        )

        for trade in open_trades:
            current_price = float(binance_client.get_ticker_price(trade.symbol)["price"])
            trade_value = trade.quantity * current_price
            entry_value = trade.quantity * trade.entry_price

            if trade.side == TradeSide.BUY:
                trade.unrealized_pnl = trade_value - entry_value
                trade.roi_percentage = ((trade_value - entry_value) / entry_value) * 100
            else:  # SELL
                trade.unrealized_pnl = entry_value - trade_value
                trade.roi_percentage = ((entry_value - trade_value) / entry_value) * 100

        db.commit()

    @staticmethod
    def calculate_performance_metrics(
        db: Session, 
        session_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> PerformanceMetrics:
        """Calculate performance metrics for paper trades"""
        # Query trades within the date range
        query = db.query(PaperTrade).filter(PaperTrade.session_id == session_id)
        if start_date:
            query = query.filter(PaperTrade.entry_time >= start_date)
        if end_date:
            query = query.filter(PaperTrade.entry_time <= end_date)
        
        trades = query.all()
        closed_trades = [t for t in trades if t.status == TradeStatus.CLOSED]

        if not closed_trades:
            return PerformanceMetrics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                total_roi_percentage=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                avg_trade_duration=0.0,
                best_trade_roi=0.0,
                worst_trade_roi=0.0,
                current_drawdown=0.0,
                risk_reward_ratio=0.0,
                profit_factor=0.0,
                avg_win_size=0.0,
                avg_loss_size=0.0,
                largest_win=0.0,
                largest_loss=0.0,
                consecutive_wins=0,
                consecutive_losses=0,
                recovery_factor=0.0
            )

        # Calculate basic metrics
        winning_trades = [t for t in closed_trades if t.realized_pnl > 0]
        losing_trades = [t for t in closed_trades if t.realized_pnl <= 0]
        
        total_pnl = sum(t.realized_pnl for t in closed_trades)
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0

        # Calculate ROI metrics
        rois = [t.roi_percentage for t in closed_trades]
        best_trade_roi = max(rois) if rois else 0
        worst_trade_roi = min(rois) if rois else 0
        total_roi = sum(rois)

        # Calculate durations
        durations = [(t.exit_time - t.entry_time).total_seconds() / 3600 for t in closed_trades]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Calculate win/loss metrics
        win_sizes = [t.realized_pnl for t in winning_trades]
        loss_sizes = [abs(t.realized_pnl) for t in losing_trades]
        
        avg_win = sum(win_sizes) / len(win_sizes) if win_sizes else 0
        avg_loss = sum(loss_sizes) / len(loss_sizes) if loss_sizes else 0
        
        largest_win = max(win_sizes) if win_sizes else 0
        largest_loss = max(loss_sizes) if loss_sizes else 0

        # Calculate risk metrics
        profit_factor = sum(win_sizes) / sum(loss_sizes) if loss_sizes else float('inf')
        risk_reward = avg_win / avg_loss if avg_loss else float('inf')

        # Calculate drawdown
        cumulative_returns = np.cumsum([t.realized_pnl for t in closed_trades])
        max_drawdown = 0
        peak = float('-inf')
        for ret in cumulative_returns:
            if ret > peak:
                peak = ret
            drawdown = (peak - ret) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)

        # Calculate consecutive trades
        consecutive_wins = 0
        consecutive_losses = 0
        current_streak = 0
        for trade in closed_trades:
            if trade.realized_pnl > 0:
                if current_streak > 0:
                    current_streak += 1
                else:
                    current_streak = 1
            else:
                if current_streak < 0:
                    current_streak -= 1
                else:
                    current_streak = -1
            consecutive_wins = max(consecutive_wins, current_streak if current_streak > 0 else 0)
            consecutive_losses = max(consecutive_losses, -current_streak if current_streak < 0 else 0)

        # Calculate Sharpe ratio (assuming risk-free rate = 0)
        returns = [t.roi_percentage/100 for t in closed_trades]
        if len(returns) > 1:
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(365) if np.std(returns) != 0 else 0
        else:
            sharpe_ratio = 0

        # Calculate recovery factor
        recovery_factor = total_pnl / max_drawdown if max_drawdown > 0 else float('inf')

        return PerformanceMetrics(
            total_trades=len(closed_trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate * 100,
            total_pnl=total_pnl,
            total_roi_percentage=total_roi,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown * 100,
            avg_trade_duration=avg_duration,
            best_trade_roi=best_trade_roi,
            worst_trade_roi=worst_trade_roi,
            current_drawdown=max_drawdown * 100,  # Current drawdown is the same as max in this case
            risk_reward_ratio=risk_reward,
            profit_factor=profit_factor,
            avg_win_size=avg_win,
            avg_loss_size=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,
            recovery_factor=recovery_factor
        )
