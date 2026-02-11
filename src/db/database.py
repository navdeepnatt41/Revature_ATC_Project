from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)
 
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)