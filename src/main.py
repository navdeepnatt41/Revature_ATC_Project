import logging
from datetime import datetime
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.domain.airport import Airport
from src.domain.exceptions import (AppErrorException,
                                   EntityAlreadyExistsException,
                                   NotFoundException,
                                   PermissionDeniedException)
from src.domain.flight import Flight, FlightStatus
from src.domain.in_flight_employee import EmployeePosition, InFlightEmployee
from src.domain.route import Route

from src.dto.flight import FlightRead
from src.dto.flight_crew import FlightCrewRead, FlightCrewScheduleRequest
from src.dto.aircraft import AircraftBase, AircraftRead
#
# Error Handling
# ---------------------------------------------
# ENABLE TO LOG
from src.loggin_config import setup_logging
from src.repositories.aircraft_repository import AircraftRepository
from src.repositories.airport_repository import AirportRepository
from src.repositories.flight_crew_repository import FlightCrewRepository
from src.repositories.flight_repository import FlightRepository
from src.repositories.in_flight_employee_repository import \
    InFlightEmployeeRepository
from src.repositories.route_repository import RouteRepository
# Change the import if we split up service
from src.services.aircraft_service import AircraftService
from src.services.flight_service import FlightService
from src.services.in_flight_employee_service import InFlightEmployeeService
from src.services.route_service import RouteService

# setup_logging()
# logger = logging.getLogger(__name__)
# # ---------------------------------------------

app = FastAPI()


# ==================================================================================================
# Repositorty Getter
# ==================================================================================================
def get_aircraft_repository(db: Session = Depends(get_db)) -> AircraftRepository:
    return AircraftRepository(db)


def get_airport_repository(db: Session = Depends(get_db)) -> AirportRepository:
    return AirportRepository(db)


def get_flight_crew_repository(db: Session = Depends(get_db)) -> FlightCrewRepository:
    return FlightCrewRepository(db)


def get_flight_repository(db: Session = Depends(get_db)) -> FlightRepository:
    return FlightRepository(db)


def get_in_flight_employee_repository(
    db: Session = Depends(get_db),
) -> InFlightEmployeeRepository:
    return InFlightEmployeeRepository(db)


def get_route_repository(db: Session = Depends(get_db)) -> RouteRepository:
    return RouteRepository(db)


# ==================================================================================================

# ==================================================================================================
# Service Getters
# ==================================================================================================

def get_aircraft_service(
    aircraft_repo: AircraftRepository = Depends(get_aircraft_repository),
    airport_repo: AirportRepository = Depends(get_airport_repository)
) -> AircraftService:
    return AircraftService(aircraft_repo, airport_repo)

def get_in_flight_employee_service(
    employee_repo: InFlightEmployeeRepository = Depends(get_in_flight_employee_repository)
) -> InFlightEmployeeService:
    return InFlightEmployeeService(employee_repo)

def get_flight_service(
    aircraft_repo: AircraftRepository = Depends(get_aircraft_repository),
    flight_crew_repo: FlightCrewRepository = Depends(get_flight_crew_repository),
    flight_repo: FlightRepository = Depends(get_flight_repository),
    in_flight_employee_repo: InFlightEmployeeRepository = Depends(get_in_flight_employee_repository),
    route_repo: RouteRepository = Depends(get_route_repository),
) -> FlightService:
    return FlightService(
        aircraft_repo,
        flight_crew_repo,
        flight_repo,
        in_flight_employee_repo,
        route_repo
    )

def get_route_service(
    airport_repo: AirportRepository = Depends(get_airport_repository),
    flight_crew_repo: FlightCrewRepository = Depends(get_flight_crew_repository),
    flight_repo: FlightRepository = Depends(get_flight_repository),
    route_repo: RouteRepository = Depends(get_route_repository),
) -> RouteService:
    return RouteService(
        airport_repo,
        flight_crew_repo,
        flight_repo,
        route_repo
    )


# ==================================================================================================
# Endpoints
# ==================================================================================================


@app.get("/status")
def status():
    return {"Status": "Ok!"}


# 
@app.get("/aircraft/available/{airport_code}", response_model=list[AircraftRead])
def available_aircraft_at_airport(
    airport_code: str,
    svc: AircraftService = Depends(get_aircraft_service)
):
    return svc.available_aircraft_at_airport(airport_code)

# Tentatively completed endpoint
# TODO
# --- Refactor to use in_flight_employee_service
@app.get("/employee/available/{airport_code}")
def availabe_employees_at_airport(
    airport_code: str,
    svc: InFlightEmployeeService = Depends(get_in_flight_employee_service)
):
    return svc.available_employees_at_airport(airport_code)


# ==================================================================================================
# Flight Operations Manager ENDPOINTS
# ==================================================================================================

# Tentatively completed
@app.put("/flight/delay/", response_model=FlightRead)
def update_flight_delay(
    flight_id: UUID,
    extra_minutes: int,
    svc: FlightService = Depends(get_flight_service),
):
    try:
        return svc.delay_flight(flight_id, extra_minutes)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while updating flight status"
        )
    

# ==================================================================================================

# ==================================================================================================
# Schedule ENDPOINTS
# ==================================================================================================

# Tentatively working
# TODO
# --- Refactor to use flight service
@app.post("/flight/schedule/", response_model=FlightRead)
def schedule_flight(
    route_id: UUID,
    aircraft_id: UUID,
    departure: datetime,
    arrival: datetime,
    svc: FlightService = Depends(get_flight_service),
):
    try:
        return svc.schedule_flight(
            route_id=route_id,
            aircraft_id=aircraft_id,
            arrival=arrival,
            departure=departure,
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))

# Tentatively working
# Refactor to use flight service
@app.post("/flight/{flight_id}/crew", response_model=list[FlightCrewRead])
def schedule_flight_crew(
    flight_id: UUID,
    payload: FlightCrewScheduleRequest,
    svc: FlightService = Depends(get_flight_service),
):
    try:
        return svc.schedule_employees(flight_id, payload.employee_ids)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))


# Tentatively completed
@app.post("/flight/launch/", response_model=FlightRead)
def launch_flight(
    flight_id: UUID, 
    svc: FlightService = Depends(get_flight_service)
):
    try:
        return svc.launch_flight(flight_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))

# Tentatively completed
@app.patch("/flight/land/", response_model=AircraftBase)
def land_flight(
    flight_id: UUID, 
    svc: FlightService = Depends(get_flight_service)
):
    try:
        return svc.confirm_flight_landed(flight_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))
# ==================================================================================================

# ==================================================================================================
# Route CRUD
# ==================================================================================================

# ==================================================================================================


# Tentatively completed endpoint
# --- Refactor to use route service
@app.get("/route/all")
def list_all_routes(svc: FlightService = Depends(get_flight_service)):
    return svc.route_list_all()


# Tentatively compoleted endpoint
# --- Refactor to use route service
@app.get("/route/{route_id}")
def get_route_by_id(
    route_id: UUID,
    svc: FlightService = Depends(get_flight_service),
):
    try:
        return svc.route_get(route_id)  # fixed service method name
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


# Tentatively completed
# --- Refactor to use route service
@app.post("/route/")
def create_route(
    origin_airport_code: str,
    destination_airport_code: str,
    svc: FlightService = Depends(get_flight_service),
):
    try:
        return svc.route_create(origin_airport_code, destination_airport_code)
    except NotFoundException as e:  # if any airport given does not exist
        raise HTTPException(status_code=404, detail=str(e))
    except EntityAlreadyExistsException as e:  # if proposed route already exists
        raise HTTPException(status_code=409, detail=str(e))


# Tentaivley completed
# --- Refactor to use route service
@app.get("/route/deletion_proposal/{route_id}")
def route_deletion_proposal(
    route_id: str, svc: FlightService = Depends(get_flight_service)
):
    return svc.route_repo.deletion_proposal(route_id)

# Works
AUTHORIZATION = "authorized"

# Tentatively works
# --- Refactor to use route service
@app.delete("/route/{route_id}")
def delete_route(
    route_id: UUID,
    authorization_code: str,
    svc: FlightService = Depends(get_flight_service),
):
    if authorization_code != AUTHORIZATION:
        raise HTTPException(
            status_code=400, detail="Permission denied: not authorized to delete routes"
        )
    return svc.route_delete(route_id)


# ==================================================================================================
# Cancelling Flights
# ==================================================================================================
# Tentatively completed 
@app.put("/flight/cancel", response_model=FlightRead)
def update_flight_cancel(
    flight_id: UUID,
    svc: FlightService = Depends(get_flight_service),
):
    try:
        return svc.cancel_flight(flight_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))
# ==================================================================================================

# ==================================================================================================
# Update Aircraft for Flight
# ==================================================================================================

# ==================================================================================================

# Tentatively completed
@app.put("/flight/replace", response_model=FlightRead)
def change_aircraft_for_flight(
    flight_id: UUID,
    aircraft_id: UUID,
    svc: FlightService = Depends(get_flight_service),
):
    try:
        updated_flight = svc.change_aircraft_for_flight(flight_id, aircraft_id)
        return updated_flight
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
         raise HTTPException(
        status_code=500,
        detail=str(e)
        )   

# Tentatively completed
@app.patch("/aircraft/fix/", response_model=AircraftBase)
def fix_aircraft(
    aircraft_id: UUID, 
    svc: AircraftService = Depends(get_aircraft_service)
):
    return svc.repair_aircraft(aircraft_id)


@app.delete("/aircraft/{route_id}")
def decommission_aircraft(
    aircraft_id: UUID, 
    authorization_code: str,
    svc: AircraftService = Depends(get_aircraft_service)
):
    try:
        if authorization_code != AUTHORIZATION:
            raise HTTPException(
                status_code=400, detail="Permission denied: not authorized to delete routes"
            )
        return svc.decommission_aircraft(aircraft_id)
    except Exception as e:
         raise HTTPException(
        status_code=500,
        detail=str(e)
        )   
    

    
    

# Stretch goal endpoints:
