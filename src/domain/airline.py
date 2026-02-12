from sqlalchemy import Column, String
from src.base import Base
    
class Airline(Base):
    __tablename__ = 'airline'

    airline_designator = Column(String, primary_key=True, nullable=True)
    name = Column(String, nullable=False)

    def __str__(self):
        return f"Airline(designator={self.airline_designator}, name={self.name})"
        