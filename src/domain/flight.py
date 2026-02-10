from datetime import datetime
import uuid
from dataclasses import dataclass
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from src.base import Base
from enum import Enum

class FlightStatus(Enum):
    SCHEDULED = "Scheduled"
    BOARDING = "Boarding"
    DEPARTED = "Departed"
    EN_ROUTE = "En_Route"
    ARRIVED = "Arrived"
    COMPLETED = "Completed"
    CANCELED = "Canceled"

@dataclass
class Flight(Base):
    __tablename__ = 'flight'
    
    flight_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(UUID(as_uuid=True), ForeignKey("route.route_id"))
    flight_status = Column(SQLEnum(FlightStatus), default=FlightStatus.SCHEDULED)
    aircraft_id = Column(UUID(as_uuid=True), ForeignKey("aircraft.aircraft_id"))
    arrival_time = Column(DateTime)
    dept_time = Column(DateTime)
    


