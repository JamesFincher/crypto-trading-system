from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime
from models.performance_log import PerformanceLog
from models.trading_crew import TradingCrew
from fastapi import HTTPException, status

class LogsService:
    def __init__(self, db: Session):
        self.db = db

    def get_performance_logs(
        self, 
        crew_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[PerformanceLog]:
        """
        Get performance logs with optional filtering.
        
        Args:
            crew_id: Optional ID of the trading crew to filter by
            start_date: Optional start date for filtering logs
            end_date: Optional end date for filtering logs
            
        Returns:
            List of PerformanceLog records matching the criteria
            
        Raises:
            HTTPException: If the specified trading crew is not found
        """
        query = self.db.query(PerformanceLog)

        if crew_id:
            # Verify crew exists
            crew = self.db.query(TradingCrew).filter(TradingCrew.id == crew_id).first()
            if not crew:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Trading crew not found"
                )
            query = query.filter(PerformanceLog.crew_id == crew_id)

        if start_date:
            query = query.filter(PerformanceLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(PerformanceLog.timestamp <= end_date)

        return query.all()

    def get_trading_metrics(
        self,
        crew_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get trading metrics for a specific crew within an optional date range.
        
        Args:
            crew_id: ID of the trading crew
            start_date: Optional start date for calculating metrics
            end_date: Optional end date for calculating metrics
            
        Returns:
            Dictionary containing calculated trading metrics:
                - profit: Total profit/loss
                - win_rate: Percentage of winning trades
                - max_drawdown: Maximum drawdown percentage
                - sharpe_ratio: Risk-adjusted return metric
                
        Raises:
            HTTPException: If the specified trading crew is not found
        """
        # Verify crew exists
        crew = self.db.query(TradingCrew).filter(TradingCrew.id == crew_id).first()
        if not crew:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trading crew not found"
            )

        # Get performance logs for the specified period
        logs = self.get_performance_logs(crew_id, start_date, end_date)
        
        # Calculate metrics
        total_trades = len(logs)
        if total_trades == 0:
            return {
                "profit": 0.0,
                "win_rate": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0
            }

        winning_trades = sum(1 for log in logs if log.profit > 0)
        total_profit = sum(log.profit for log in logs)
        
        # Calculate win rate
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Simple max drawdown calculation
        cumulative_profit = 0
        peak = 0
        max_drawdown = 0
        
        for log in logs:
            cumulative_profit += log.profit
            peak = max(peak, cumulative_profit)
            drawdown = (peak - cumulative_profit) / peak * 100 if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)

        return {
            "profit": total_profit,
            "win_rate": win_rate,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": 0.0  # TODO: Implement Sharpe ratio calculation
        }
