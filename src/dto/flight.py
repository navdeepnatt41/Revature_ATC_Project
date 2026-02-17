"""
Data Transfer Objects (DTOs) for Flight entities.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FlightStatus(str, Enum):
    """
    Operational states of a flight lifecycle.
    """

    SCHEDULED = "SCHEDULED"
    IN_FLIGHT = "IN-FLIGHT"
    ARRIVED = "ARRIVED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"


class FlightCreate(BaseModel):
    """
    Data schema for initializing a new flight record.
    """

    route_id: UUID = Field(..., description="ID of the predefined flight route")
    flight_status: FlightStatus = Field(
        FlightStatus.SCHEDULED, description="Initial flight state"
    )
    aircraft_id: UUID = Field(
        ..., description="ID of the aircraft assigned to the flight"
    )
    arrival_time: str = Field(
        None, description="Projected arrival timestamp"
    )
    departure_time: str = Field(
        None, description="Projected departure timestamp"
    )


class FlightRead(BaseModel):
    """
    Data schema for flight information retrieved from the database.
    """

    flight_id: UUID = Field(
        ..., description="Unique database identifier for the flight"
    )
    route_id: UUID | None = Field(..., description="Foreign key to the associated route")
    flight_status: FlightStatus | None = Field(..., description="Current operational status")
    aircraft_id: UUID | None = Field(..., description="Foreign key to the assigned aircraft")
    arrival_time: datetime | None = Field(
        None, description="Actual or projected arrival time"
    )
    departure_time: datetime | None = Field(
        None, description="Actual or projected departure time"
    )

    model_config = ConfigDict(from_attributes=True)

class FlightDelay(BaseModel):
    """
    Data schema for a user to supply a delay for a flight 
    """
    flight_id: UUID = Field(
        ..., description = "Unique flight identifier"
    )
    
    extra_minutes: int = Field(
        ..., description = "Minutes to delay a flight by"
    )

class Flight_ID(BaseModel):
    """
    Data schema for a user who wishes to launch a flight
    """

    flight_id: UUID = Field(
        ..., description = "Unique flight identifier"
    )