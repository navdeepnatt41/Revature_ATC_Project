import uuid
from dataclasses import dataclass
from sqlalchemy import Column, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from src.base import Base
from enum import Enum

class FlightStatus(Enum):
    SCHEDULED = "SCHEDULED"
    IN_FLIGHT = "IN-FLIGHT"
    ARRIVED = "ARRIVED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"

@dataclass
class Flight(Base):
    __tablename__ = 'flight'
    
    flight_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(UUID(as_uuid=True), ForeignKey("route.route_id"), nullable=False)
    flight_status = Column(SQLEnum(FlightStatus), default=FlightStatus.SCHEDULED)
    aircraft_id = Column(UUID(as_uuid=True), ForeignKey("aircraft.aircraft_id"), nullable=False)
    arrival_time = Column(DateTime)
    departure_time = Column(DateTime)
    


