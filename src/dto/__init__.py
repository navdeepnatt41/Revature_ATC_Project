"""
The dto module defines the Pydantic models for all of the domain objects. It will serve to verify 
types for attributes, do type conversions, and enables serialization/de-serialization.
"""

from .aircraft import *
from .airport import *
from .flight_crew import *
from .flight import *
from .in_flight_employee import *
from .route import *

__all__ = [
    "AircraftStatus",
    "AircraftCreate",
    "AircraftRead",
    "AirportCreate",
    "AirportRead",
    "FlightCrewCreate",
    "FlightCrewRead",
    "FlightCrewScheduleRequest",
    "FlightCreate",
    "FlightRead"
    "FlightStatus",
    "EmployeePosition",
    "InFlightStatus",
    "InFlightEmployeeCreate",
    "InFlightEmployeeRead"
]