from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
