from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.user import User
from models.trading_crew import TradingCrew
from schemas.trading import TradingCrewCreate, TradingCrewResponse
from services.trading_crew_service import TradingCrewService
from utils.dependencies import get_current_user

router = APIRouter()

@router.post("/crews", response_model=TradingCrewResponse, status_code=status.HTTP_201_CREATED)
def create_trading_crew(
    crew: TradingCrewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TradingCrewResponse:
    """
    Create a new trading crew
    
    Args:
        crew: Trading crew data
        db: Database session
        current_user: Currently authenticated user
        
    Returns:
        Created trading crew
    """
    service = TradingCrewService(db)
    return service.create_crew(crew, current_user.id)

@router.get("/crews", response_model=List[TradingCrewResponse])
def get_trading_crews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[TradingCrewResponse]:
    """
    Get all trading crews
    
    Args:
        db: Database session
        current_user: Currently authenticated user
        
    Returns:
        List of trading crews
    """
    service = TradingCrewService(db)
    return service.get_crews(current_user.id)

@router.get("/crews/{crew_id}", response_model=TradingCrewResponse)
def get_trading_crew(
    crew_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TradingCrewResponse:
    """
    Get a specific trading crew
    
    Args:
        crew_id: ID of the crew to get
        db: Database session
        current_user: Currently authenticated user
        
    Returns:
        Trading crew if found
        
    Raises:
        HTTPException: If crew not found
    """
    service = TradingCrewService(db)
    crew = service.get_crew(crew_id, current_user.id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trading crew not found"
        )
    return crew

@router.put("/crews/{crew_id}/activate", response_model=TradingCrewResponse)
def activate_trading_crew(
    crew_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TradingCrewResponse:
    """
    Activate a trading crew
    
    Args:
        crew_id: ID of the crew to activate
        db: Database session
        current_user: Currently authenticated user
        
    Returns:
        Updated trading crew
        
    Raises:
        HTTPException: If crew not found
    """
    service = TradingCrewService(db)
    crew = service.activate_crew(crew_id, current_user.id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trading crew not found"
        )
    return crew

@router.put("/crews/{crew_id}/deactivate", response_model=TradingCrewResponse)
def deactivate_trading_crew(
    crew_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TradingCrewResponse:
    """
    Deactivate a trading crew
    
    Args:
        crew_id: ID of the crew to deactivate
        db: Database session
        current_user: Currently authenticated user
        
    Returns:
        Updated trading crew
        
    Raises:
        HTTPException: If crew not found
    """
    service = TradingCrewService(db)
    crew = service.deactivate_crew(crew_id, current_user.id)
    if not crew:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trading crew not found"
        )
    return crew
