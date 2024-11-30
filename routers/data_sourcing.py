from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from database import get_db
from services.data_sourcing_service import DataSourcingService
from schemas.data_sourcing import DataFetchRequest, DataFetchResponse
from utils.auth_utils import get_current_user

router = APIRouter(
    prefix="/data-sourcing",
    tags=["Data Sourcing"]
)

@router.post("/fetch", response_model=DataFetchResponse)
async def fetch_data(
    request: DataFetchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict:
    """
    Fetch and store market data for a trading crew.
    
    Args:
        request: Data fetch request containing crew_id, time range, and intervals
        db: Database session
        current_user: Currently authenticated user
        
    Returns:
        Dictionary containing the fetched data for each symbol and interval
    """
    service = DataSourcingService(db)
    return await service.fetch_data(
        crew_id=request.crew_id,
        start_time=request.start_time,
        end_time=request.end_time,
        intervals=request.intervals
    )
