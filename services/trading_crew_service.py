from sqlalchemy.orm import Session
from typing import List, Optional
from models.trading_crew import TradingCrew
from schemas.trading import TradingCrewCreate

class TradingCrewService:
    def __init__(self, db: Session):
        self.db = db

    def create_crew(self, crew_data: TradingCrewCreate, user_id: int) -> TradingCrew:
        """
        Create a new trading crew
        
        Args:
            crew_data: Trading crew data
            user_id: ID of the user creating the crew
            
        Returns:
            Created trading crew
        """
        crew = TradingCrew(
            name=crew_data.name,
            user_id=user_id,
            strategy_config=crew_data.strategy_config,
            trading_pairs=crew_data.trading_pairs,
            risk_percentage=crew_data.risk_percentage,
            max_position_size=crew_data.max_position_size,
            is_active=False
        )
        self.db.add(crew)
        self.db.commit()
        self.db.refresh(crew)
        return crew

    def get_crews(self, user_id: int) -> List[TradingCrew]:
        """
        Get all trading crews for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of trading crews
        """
        return self.db.query(TradingCrew).filter(TradingCrew.user_id == user_id).all()

    def get_crew(self, crew_id: int, user_id: int) -> Optional[TradingCrew]:
        """
        Get a specific trading crew
        
        Args:
            crew_id: ID of the crew
            user_id: ID of the user
            
        Returns:
            Trading crew if found, None otherwise
        """
        return self.db.query(TradingCrew).filter(
            TradingCrew.id == crew_id,
            TradingCrew.user_id == user_id
        ).first()

    def activate_crew(self, crew_id: int, user_id: int) -> TradingCrew:
        """
        Activate a trading crew
        
        Args:
            crew_id: ID of the crew
            user_id: ID of the user
            
        Returns:
            Updated trading crew
            
        Raises:
            ValueError: If crew not found
        """
        crew = self.get_crew(crew_id, user_id)
        if not crew:
            raise ValueError("Trading crew not found")
        
        crew.is_active = True
        self.db.commit()
        self.db.refresh(crew)
        return crew

    def deactivate_crew(self, crew_id: int, user_id: int) -> TradingCrew:
        """
        Deactivate a trading crew
        
        Args:
            crew_id: ID of the crew
            user_id: ID of the user
            
        Returns:
            Updated trading crew
            
        Raises:
            ValueError: If crew not found
        """
        crew = self.get_crew(crew_id, user_id)
        if not crew:
            raise ValueError("Trading crew not found")
        
        crew.is_active = False
        self.db.commit()
        self.db.refresh(crew)
        return crew
