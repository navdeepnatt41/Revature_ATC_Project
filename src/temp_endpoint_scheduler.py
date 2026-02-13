from fastapi import FastAPI, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.orm import Session

from src.db.deps import get_db

from src.domain.exceptions import PermissionDeniedException

from src.domain.airport import Airport
from src.domain.route import Route
from src.domain.flight import Flight
from src.domain.in_flight_employee import InFlightEmployee, EmployeePosition
from src.repositories.airport_repository import AirportRepository
from src.repositories.route_repository import RouteRepository
from src.repositories.flight_repository import FlightRepository
from src.repositories.in_flight_employee_repository import InFlightEmployeeRepository
from src.services.in_flight_employee_service import InFlightEmployeeService
from src.services.customer_service import CustomerService
from src.services.hr_employee_service import HRemployeeService
from src.services.route_service import RouteService
from src.dto.flight import FlightRead

# As a scheduler, I want to assign aircraft to flights based on availability and route requirements
# potentially adding availability status for Aircraft
@app.post("/scheduler/assign_aircraft")

# 1. Listing all available aircraft at an airport at a certain time 
# 2. CRUD (create) for flight (schedule)

def find_available_aircraft(srv, flight):
    # The idea of this method is to find all aircraft available for a Flight during its instantiation
    # So while creating a flight, this method needs to be called before an aircraft_id is set for the flight object

    # Potential issue: does this method become an internal function instead of an endpoint? Or will it be
    #                   called as an endpoint internally? This method cannot be called unless a Flight is being made



    # We can find aircraft available at a certain airport
    #   We need to know which flight we are searching an aircraft for
    #   Then, we get two target details: target airport and target time
    #       Target airport: origin airport of the flight's route (flight > route_id > Route > origin_airport_code)
    #       Target time: departure time of the flight (flight > dept_time)
    #