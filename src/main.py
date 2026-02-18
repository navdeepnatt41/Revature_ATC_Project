from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.domain.exceptions import (
    AppErrorException,
    EntityAlreadyExistsException,
    NotFoundException,
    PermissionDeniedException,
)

from src.dto.flight import Flight_ID, FlightCreate, FlightRead, FlightDelay
from src.dto.flight_crew import FlightCrewRead, FlightCrewScheduleRequest
from src.dto.aircraft import Aircraft_ID, AircraftBase, AircraftChange, AircraftRead
from src.dto.airport import AirportRead
from src.dto.in_flight_employee import InFlightEmployeeRead

from src.dto.route import RouteCreate, RouteDelete, RouteRead
from src.services.visualization_service import available_charts, render_chart_png

from src.repositories.aircraft_repository import AircraftRepository
from src.repositories.airport_repository import AirportRepository
from src.repositories.flight_crew_repository import FlightCrewRepository
from src.repositories.flight_repository import FlightRepository
from src.repositories.in_flight_employee_repository import InFlightEmployeeRepository
from src.repositories.route_repository import RouteRepository

from src.services.aircraft_service import AircraftService
from src.services.flight_service import FlightService
from src.services.in_flight_employee_service import InFlightEmployeeService
from src.services.route_service import RouteService

# setup_logging()
# logger = logging.getLogger(__name__)
# # ---------------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    airport_repo: AirportRepository = Depends(get_airport_repository),
) -> AircraftService:
    return AircraftService(aircraft_repo, airport_repo)


def get_in_flight_employee_service(
    employee_repo: InFlightEmployeeRepository = Depends(
        get_in_flight_employee_repository
    ),
    airport_repo: AirportRepository = Depends(get_airport_repository),
) -> InFlightEmployeeService:
    return InFlightEmployeeService(employee_repo, airport_repo)


def get_flight_service(
    aircraft_repo: AircraftRepository = Depends(get_aircraft_repository),
    airport_repo: AirportRepository = Depends(get_airport_repository),
    flight_crew_repo: FlightCrewRepository = Depends(get_flight_crew_repository),
    flight_repo: FlightRepository = Depends(get_flight_repository),
    in_flight_employee_repo: InFlightEmployeeRepository = Depends(
        get_in_flight_employee_repository
    ),
    route_repo: RouteRepository = Depends(get_route_repository),
) -> FlightService:
    return FlightService(
        aircraft_repo,
        airport_repo,
        flight_crew_repo,
        flight_repo,
        in_flight_employee_repo,
        route_repo,
    )


def get_route_service(
    airport_repo: AirportRepository = Depends(get_airport_repository),
    flight_crew_repo: FlightCrewRepository = Depends(get_flight_crew_repository),
    flight_repo: FlightRepository = Depends(get_flight_repository),
    route_repo: RouteRepository = Depends(get_route_repository),
) -> RouteService:
    return RouteService(airport_repo, flight_crew_repo, flight_repo, route_repo)


# ==================================================================================================
# Endpoints
# ==================================================================================================


@app.get("/status")
def status():
    return {"Status": "Ok!"}


@app.get("/flight/all", response_model=list[FlightRead])
def list_all_flights(repo: FlightRepository = Depends(get_flight_repository)):
    return repo.list_all()


@app.get("/airport/all", response_model=list[AirportRead])
def list_all_airports(repo: AirportRepository = Depends(get_airport_repository)):
    return repo.list_all()


@app.get("/aircraft/all", response_model=list[AircraftRead])
def list_all_aircraft(repo: AircraftRepository = Depends(get_aircraft_repository)):
    return repo.list_all()


# ==================================================================================================
# Flight ENDPOINTS
# ==================================================================================================


@app.post("/flight/schedule/", response_model=FlightRead)
def schedule_flight(
    payload: FlightCreate,
    svc: FlightService = Depends(get_flight_service),
):
    try:
        return svc.schedule_flight(
            route_id=payload.route_id,
            aircraft_id=payload.aircraft_id,
            arrival=payload.arrival_time,
            departure=payload.departure_time,
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while scheduling"
        )


@app.post("/flight/crew", response_model=list[FlightCrewRead])
def schedule_flight_crew(
    payload: FlightCrewScheduleRequest,
    svc: FlightService = Depends(get_flight_service),
):
    try:
        return svc.schedule_employees(payload.flight_id, payload.employee_ids)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while assigning flight crew"
        )


@app.patch("/flight/replace/", response_model=FlightRead)
def change_aircraft_for_flight(
    payload: AircraftChange,
    svc: FlightService = Depends(get_flight_service),
):
    try:
        updated_flight = svc.change_aircraft_for_flight(
            payload.flight_id, payload.aircraft_id
        )
        return updated_flight
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while changing aircraft"
        )


@app.patch("/flight/delay/", response_model=FlightRead)
def update_flight_delay(
    payload: FlightDelay, svc: FlightService = Depends(get_flight_service)
):
    try:
        return svc.delay_flight(payload.flight_id, payload.extra_minutes)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while delaying flight"
        )


@app.patch("/flight/cancel", response_model=FlightRead)
def update_flight_cancel(
    payload: Flight_ID,
    svc: FlightService = Depends(get_flight_service),
):
    try:
        return svc.cancel_flight(payload.flight_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while canceling flight"
        )


@app.patch("/flight/launch/", response_model=FlightRead)
def launch_flight(payload: Flight_ID, svc: FlightService = Depends(get_flight_service)):
    try:
        return svc.launch_flight(payload.flight_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while launching flight"
        )


@app.patch("/flight/land/", response_model=AircraftBase)
def land_flight(payload: Flight_ID, svc: FlightService = Depends(get_flight_service)):
    try:
        return svc.confirm_flight_landed(payload.flight_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================================================================================================
# Route Endpoints
# ==================================================================================================


@app.get("/route/all", response_model=list[RouteRead])
def list_all_routes(svc: RouteService = Depends(get_route_service)):
    try:
        return svc.route_list_all()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while listing flights"
        )


@app.get("/route/{route_id}", response_model=RouteRead)
def get_route_by_id(
    route_id: UUID,
    svc: RouteService = Depends(get_route_service),
):
    try:
        return svc.route_get(route_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while getting route"
        )


@app.post("/route/")
def create_route(
    payload: RouteCreate,
    svc: RouteService = Depends(get_route_service),
):
    try:
        return svc.route_create(
            payload.origin_airport_code, payload.destination_airport_code
        )
    except NotFoundException as e:  # if any airport given does not exist
        raise HTTPException(status_code=404, detail=str(e))
    except EntityAlreadyExistsException as e:  # if proposed route already exists
        raise HTTPException(status_code=409, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while creating route"
        )


@app.get("/route/deletion_proposal/{route_id}")
def route_deletion_proposal(
    route_id: UUID, svc: RouteService = Depends(get_route_service)
):
    try:
        return svc.deletion_proposal(route_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while finding employees and flights",
        )


AUTHORIZATION = "authorized"


@app.delete("/route")
def delete_route(
    payload: RouteDelete,
    svc: RouteService = Depends(get_route_service),
):
    if payload.authorization_code != AUTHORIZATION:
        raise HTTPException(
            status_code=400, detail="Permission denied: not authorized to delete routes"
        )
    try:
        return svc.route_delete(payload.route_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while deleting route"
        )


# ==================================================================================================
# Employee Endpoints
# ==================================================================================================


@app.get(
    "/employee/available/{airport_code}", response_model=list[InFlightEmployeeRead]
)
def available_employees_at_airport(
    airport_code: str,
    svc: InFlightEmployeeService = Depends(get_in_flight_employee_service),
):
    try:
        return svc.available_employees_at_airport(airport_code)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while finding available employees",
        )


# ==================================================================================================
# Aircraft Endpoints
# ==================================================================================================


@app.patch("/aircraft/fix/", response_model=AircraftBase)
def fix_aircraft(
    payload: Aircraft_ID, svc: AircraftService = Depends(get_aircraft_service)
):
    try:
        return svc.repair_aircraft(payload.aircraft_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while fixing aircraft"
        )


@app.patch("/aircraft/schedule_repair/", response_model=AircraftBase)
def schedule_repair_aircraft(
    payload: Aircraft_ID, svc: AircraftService = Depends(get_aircraft_service)
):
    try:
        return svc.schedule_repair_aircraft(payload.aircraft_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while scheduling aircraft for repair",
        )


@app.get("/aircraft/available/{airport_code}", response_model=list[AircraftRead])
def available_aircraft_at_airport(
    airport_code: str, svc: AircraftService = Depends(get_aircraft_service)
):
    try:
        return svc.available_aircraft_at_airport(airport_code)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except AppErrorException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while finding available aircrafts",
        )


@app.get("/visualizations")
def list_visualizations():
    return {"charts": available_charts()}


@app.get("/visualizations/{chart_name}.png")
def get_visualization_chart(chart_name: str):
    try:
        png_bytes = render_chart_png(chart_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(content=png_bytes, media_type="image/png")
