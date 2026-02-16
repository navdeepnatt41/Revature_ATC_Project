"""
Defines the Flight SQLAlchemy ORM for the application
"""

import uuid
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.base import Base


class FlightStatus(Enum):
    """
    Enum that defines the different status a flight can have

    Attributes:
        SCHEDULED (str): A flight is scheduled to depart
        IN_FLIGHT (str): A flight is currently in progess
        ARRIVED (str): A flight has successfully completed
        DELAYED (str): A flight has been delayed
        CANCELLED (str): A flight has been cancelled
    """

    SCHEDULED = "SCHEDULED"
    IN_FLIGHT = "IN-FLIGHT"
    ARRIVED = "ARRIVED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"


@dataclass
class Flight(Base):
    """
    The Flight ORM for the Flight table

    Attributes:
        flight_id (UUID): The UUID value which uniquely identifies a flight
        route_id (UUID): The UUID value which uniquely identifies the route this flight is flying
        flight_status (FlightStatus): The status of the flight
        aircraft_id (UUID): The UUID value for the aircraft that is operating this flight
        arrival_time (datetime): Arrival time
        departure_time (datetime): Departure time
    """

    __tablename__ = "flight"

    flight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    route_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("route.route_id"), nullable=False
    )
    flight_status: Mapped[FlightStatus] = mapped_column(
        SQLEnum(FlightStatus), default=FlightStatus.SCHEDULED
    )
    aircraft_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("aircraft.aircraft_id"), nullable=False
    )
    arrival_time: Mapped[datetime] = mapped_column(DateTime)
    departure_time: Mapped[datetime] = mapped_column(DateTime)
