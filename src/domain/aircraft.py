import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from src.base import Base
from enum import Enum

class AircraftStatus(Enum):
    AVAILABLE = "AVAILABLE"
    DEPLOYED = "DEPLOYED"
    AOG = "MAINTENANCE"

class Aircraft(Base):
    __tablename__ = "aircraft"

    aircraft_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    #airline_designator = Column(String, ForeignKey("airline.airline_designator"), nullable=False)

    manufacturer = Column(String)
    aircraft_model = Column(String)
    current_distance = Column(Float)
    maintenance_interval = Column(Float)
    aircraft_status = Column(SQLEnum(AircraftStatus))

    aircraft_location = Column(String, ForeignKey('airport.airport_code'), nullable=False)