from datetime import datetime
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

# Change the import if we split up service
from src.services.flight_operation_service import FlightOperationService

from src.domain.in_flight_employee import InFlightEmployee, EmployeePosition
from src.domain.exceptions import PermissionDeniedException, NotFoundException, AppErrorException, EntityAlreadyExistsException
from src.domain.airport import Airport
from src.domain.route import Route
from src.domain.flight import Flight, FlightStatus

from src.dto.flight import FlightRead
from src.dto.flight_crew import FlightCrewRead, FlightCrewScheduleRequest

#
# Error Handling
# ---------------------------------------------
# ENABLE TO LOG
# from src.loggin_config import setup_logging
# import logging

# setup_logging()
# logger = logging.getLogger(__name__)
# ---------------------------------------------

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


def get_flight_operation_service(
    aircraft_repo: AircraftRepository = Depends(get_aircraft_repository),
    airport_repo: AirportRepository = Depends(get_airport_repository),
    flight_crew_repo: FlightCrewRepository = Depends(get_flight_crew_repository),
    flight_repo: FlightRepository = Depends(get_flight_repository),
    in_flight_employee_repo: InFlightEmployeeRepository = Depends(
        get_in_flight_employee_repository
    ),
    route_repo: RouteRepository = Depends(get_route_repository),
) -> FlightOperationService:
    return FlightOperationService(
        aircraft_repo,
        airport_repo,
        flight_crew_repo,
        flight_repo,
        in_flight_employee_repo,
        route_repo,
    )


# ==================================================================================================
# Endpoints
# ==================================================================================================

# Tentatively completed endpoint
@app.get("/aircraft/available/{airport_code}")
def available_aircraft_at_airport(airport_code: str, svc: FlightOperationService =  Depends(get_flight_operation_service)):
    return svc.aircraft_repo.availabe_aircraft_by_airport(airport_code)
    
# Tentatively completed endpoint
@app.get("/employee/available/{airport_code}")
def availabe_employees_at_airport(airport_code: str, svc: FlightOperationService = Depends(get_flight_operation_service)):
    return svc.in_flight_employee_repo.available_employees_at_airport(airport_code)

# ==================================================================================================
# Flight Operations Manager ENDPOINTS
# ==================================================================================================

@app.put("/flight/{flight_id}/delay")
def update_flight_delay(flight_id: UUID, new_status: str, extra_minutes: int,  svc: FlightOperationService = Depends(get_flight_operation_service)):
    try:
        new_status_enum = FlightStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid flight status value")
    
    try:
        updated_flight = svc.update_flight_status(flight_id, new_status_enum)
        updated_flight = svc.delay_flight(flight_id,extra_minutes)

        return updated_flight
       
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while updating flight status")

# ==================================================================================================

# ==================================================================================================
# Schedule ENDPOINTS
# ==================================================================================================

@app.post("/flight/schedule", response_model = FlightRead)
def schedule_flight(
    route_id: UUID,
    aircraft_id: UUID,
    departure: datetime,
    arrival: datetime,
    svc: FlightOperationService = Depends(get_flight_operation_service)
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
    
@app.post("/flight/{flight_id}/crew", response_model=list[FlightCrewRead])
def schedule_flight_crew(
    flight_id: UUID,
    payload: FlightCrewScheduleRequest,
    svc: FlightOperationService = Depends(get_flight_operation_service),
):
    try:
        return svc.schedule_employees(flight_id, payload.employee_ids)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/flight/launch") ## <<< JUAN working on this
def launch_flight(
    flight_id: UUID,
    svc: FlightOperationService = Depends(get_flight_operation_service)
):
    try:
        # Check if flight has a flight crew
        flight_crew = svc.flight_crew_repo.get_by_flight_id(flight_id)
        if not flight_crew:
            raise PermissionDeniedException("Flight cannot depart without a flight crew assigned")
        
        # Check if flight crew has required positions
        required_positions = {
            EmployeePosition.CAPTAIN,
            EmployeePosition.COPILOT,
            EmployeePosition.FLIGHT_MANAGER,
            EmployeePosition.FLIGHT_ATTENDANT
        }
        
        crew_positions = {member.position for member in flight_crew.members}
        
        if not required_positions.issubset(crew_positions):
            missing_positions = required_positions - crew_positions
            raise PermissionDeniedException(
                f"Flight cannot depart. Missing positions: {', '.join([p.value for p in missing_positions])}"
            )
        
        # Update flight status to DEPARTED
        updated_flight = svc.update_flight_status(flight_id, FlightStatus.IN_FLIGHT)
        
        return updated_flight
        
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while launching flight")
    



# ==================================================================================================

# ==================================================================================================
# Route CRUD
# ==================================================================================================

# ==================================================================================================

# Tentatively completed endpoint
@app.get("/route/all")
def test(svc: FlightOperationService = Depends(get_flight_operation_service)):
    return svc.route_list_all()

# Tentatively compoleted endpoint
# 3) Fix route get endpoint call
@app.get("/route/{route_id}")
def get_route_by_id(
    route_id: UUID,
    svc: FlightOperationService = Depends(get_flight_operation_service),
):
    try:
        return svc.route_get(route_id)  # fixed service method name
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/route")
def create_route(origin_airport_code: str, destination_airport_code: str, svc: FlightOperationService = Depends(get_flight_operation_service)):
    try:
        return svc.route_create(origin_airport_code, destination_airport_code)
    except NotFoundException as e: # if any airport given does not exist
        raise HTTPException(status_code=404, detail=str(e))
    except EntityAlreadyExistsException as e: # if proposed route already exists
        raise HTTPException(status_code=409, detail=str(e))

@app.put("/route/{route_id}")
def update_route(route_id: UUID, origin_airport_code: str, destination_airport_code: str, svc: FlightOperationService = Depends(get_flight_operation_service)):
    try:
        return svc.route_update(route_id, origin_airport_code, destination_airport_code)
    except NotFoundException as e: # if either or both airports do not exist
        raise HTTPException(status_code=404, detail=str(e))
    except EntityAlreadyExistsException as e: # if proposed route already exists
        raise HTTPException(status_code=409, detail=str(e))

# Tentaivley completed, NEEDS MORE TESTING
@app.get("/route/deletion_proposal/{route_id}")
def route_deletion_proposal(route_id: str, svc: FlightOperationService = Depends(get_flight_operation_service)):
    return svc.route_repo.deletion_proposal(route_id)

AUTHORIZATION = "authorized"
@app.delete("/route/{route_id}")
def delete_route(route_id: UUID, authorization_code: str, svc: FlightOperationService = Depends(get_flight_operation_service)):
    if authorization_code != AUTHORIZATION:
        raise HTTPException(status_code=400, detail="Permission denied: not authorized to delete routes")
    return svc.route_delete(route_id)

# ==================================================================================================
# Cancelling Flights
# ==================================================================================================
@app.put("/flight/{flight_id}/cancel")
def update_flight_cancel(
    flight_id: UUID,
    svc: FlightOperationService = Depends(get_flight_operation_service),
):
    try:
        return svc.update_flight_status(flight_id, FlightStatus.CANCELLED)
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while updating flight status")
    
# ==================================================================================================

# ==================================================================================================
# Update Aircraft for Flight
# ==================================================================================================

# ==================================================================================================
@app.put("/flight/{flight_id}/replace")
def change_aircraft_for_flight(flight_id : UUID, aircraft_id: UUID, svc: FlightOperationService = Depends(get_flight_operation_service) ):
    try:
        updated_flight = svc.change_aircraft_for_flight(flight_id, aircraft_id)
        return updated_flight
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while updating flight status")

# Stretch goal endpoints:



