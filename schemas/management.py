from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class OptimizationRequest(BaseModel):
    crew_id: int
    strategy_params: Dict[str, List[float]]  # Parameters to optimize and their ranges
    optimization_metric: str  # e.g., "sharpe_ratio", "total_pnl"
    start_date: datetime
    end_date: datetime
    max_iterations: Optional[int] = 100

class OptimizationResponse(BaseModel):
    crew_id: int
    status: str
    best_params: Dict[str, float]
    metric_value: float
    iterations_completed: int
    optimization_time: float

class SystemStatus(BaseModel):
    status: str
    active_crews: int
    total_crews: int
    system_load: float
    last_backup: Optional[datetime] = None

class BackupResponse(BaseModel):
    backup_id: str
    timestamp: datetime
    size_bytes: int
    status: str
