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

    manufacturer = Column(String, nullable=True)
    aircraft_model = Column(String, nullable=True)
    current_distance = Column(Float, nullable=False)
    maintenance_interval = Column(Float, nullable=False)
    aircraft_status = Column(SQLEnum(AircraftStatus), default= AircraftStatus.AVAILABLE)

    aircraft_location = Column(UUID(as_uuid=True), ForeignKey('airport.airport_code'))