import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from database import Base, get_db
import os
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    """Test that we can connect to the PostgreSQL database"""
    database_url = os.getenv("DATABASE_URL")
    assert database_url is not None, "DATABASE_URL environment variable is not set"
    assert "postgresql://" in database_url, "DATABASE_URL should be a PostgreSQL connection string"
    
    try:
        # Create an engine and try to connect
        engine = create_engine(database_url)
        with engine.connect() as connection:
            # Try a simple query
            result = connection.execute(text("SELECT 1"))
            assert result.scalar() == 1, "Database query failed"
            
            # Check if we can see our database
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            assert db_name == "crypto_trading", f"Connected to wrong database: {db_name}"
            
            # Check if our main tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            required_tables = ['alembic_version', 'users', 'trading_crews']
            for table in required_tables:
                assert table in tables, f"Required table '{table}' not found in database"
            
    except OperationalError as e:
        pytest.fail(f"Failed to connect to database: {str(e)}")

def test_database_session():
    """Test that we can create a database session and perform operations"""
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with SessionLocal() as session:
            # Try to execute a transaction
            result = session.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            assert isinstance(user_count, int), "Failed to get user count from database"
            
    except Exception as e:
        pytest.fail(f"Failed to perform database operations: {str(e)}")

def test_get_db():
    """Test that our get_db dependency works"""
    try:
        db = next(get_db())
        assert db is not None, "get_db() returned None"
        
        # Try a simple query using the session
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1, "Database query through get_db() failed"
        
    except Exception as e:
        pytest.fail(f"get_db() failed: {str(e)}")
    finally:
        db.close()
