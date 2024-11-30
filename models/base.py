"""Base model for SQLAlchemy models."""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import MetaData

# Naming convention for constraints
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from class name."""
        return cls.__name__.lower()
