from fastapi import FastAPI, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.orm import Session

from src.db.deps import get_db

from src.repositories.aircraft_repository import AircraftRepository
from src.repositories.airport_repository import AirportRepository
from src.repositories.flight_crew_repository import FlightCrewRepository
from src.repositories.flight_repository import FlightRepository
from src.repositories.in_flight_employee_repository import InFlightEmployeeRepository
from src.repositories.route_repository import RouteRepository

#Change the import if we split up service
from src.services.flight_operation_service import FlightOperationService

from src.domain.in_flight_employee import InFlightEmployee, EmployeePosition
from src.domain.exceptions import PermissionDeniedException

from src.domain.airport import Airport
from src.domain.route import Route
from src.domain.flight import Flight
from src.dto.flight import FlightRead

#
# Error Handling
#---------------------------------------------
# ENABLE TO LOG
# from src.loggin_config import setup_logging
# import logging

# setup_logging()
# logger = logging.getLogger(__name__)
#---------------------------------------------

app = FastAPI()

#
# Repositorty Getter
# -------------------------------------------------------------------------------------------------
def get_aircraft_repository(db: Session = Depends(get_db)) -> AircraftRepository:
    return AircraftRepository(db)

def get_airport_repository(db: Session = Depends(get_db)) -> AirportRepository:
    return AirportRepository(db)

def get_flight_crew_repository(db: Session = Depends(get_db)) -> FlightCrewRepository:
    return FlightCrewRepository(db)

def get_flight_repository(db: Session = Depends(get_db)) -> FlightRepository:
    return FlightRepository(db)

def get_in_flight_employee_repository(db: Session = Depends(get_db)) -> InFlightEmployeeRepository:
    return InFlightEmployeeRepository(db)

def get_route_repository(db: Session = Depends(get_db)) -> RouteRepository:
    return RouteRepository(db)
# ------------------------------------------------------------------------------------------------

#
#Service Getters
# ------------------------------------------------------------------------------------------------

def get_flight_operation_service(
    aircraft_repo: AircraftRepository = Depends(get_aircraft_repository),
    airport_repo: AirportRepository = Depends(get_airport_repository),
    flight_crew_repo: FlightCrewRepository = Depends(get_flight_crew_repository),
    flight_repo: FlightRepository = Depends(get_flight_repository),
    in_flight_employee_repo: InFlightEmployeeRepository = Depends(get_in_flight_employee_repository),
    route_repo: RouteRepository = Depends(get_route_repository)
) -> FlightOperationService:
    return FlightOperationService(aircraft_repo, airport_repo, flight_crew_repo, flight_repo, in_flight_employee_repo, route_repo)



#
# Endpoints
#

@app.get("/route")
def test(
    svc : FlightOperationService = Depends(get_flight_operation_service)
):
    return svc.route_list_all()