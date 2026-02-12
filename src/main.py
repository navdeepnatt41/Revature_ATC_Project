from fastapi import FastAPI, Depends, HTTPException, Query
from uuid import UUID
from sqlalchemy.orm import Session

from src.db.deps import get_db

from src.repositories.airport_repository import AirportRepository
from src.repositories.route_repository import RouteRepository
from src.repositories.flight_repository import FlightRepository
from src.repositories.in_flight_employee_repository import InFlightEmployeeRepository
from src.services.in_flight_employee_service import InFlightEmployeeService
from src.domain.in_flight_employee import InFlightEmployee, EmployeePosition
from src.domain.exceptions import PermissionDeniedException
from src.services.customer_service import CustomerService
from src.services.hr_employee_service import HRemployeeService

from src.domain.airport import Airport
from src.domain.route import Route
from src.domain.flight import Flight

# ENABLE TO LOG
# from src.loggin_config import setup_logging
# import logging

# setup_logging()
# logger = logging.getLogger(__name__)
######################## LOG


app = FastAPI()

#Repositorty Getter
def get_flight_repository(db: Session = Depends(get_db)) -> FlightRepository:
    return FlightRepository(db)

def get_route_repository(db: Session = Depends(get_db)) -> RouteRepository:
    return RouteRepository(db)

def get_airport_repository(db: Session = Depends(get_db)) -> AirportRepository:
    return AirportRepository(db)

#Service Getters
def get_customer_service(flight_repo: FlightRepository = Depends(get_flight_repository),
                         route_repo: RouteRepository = Depends(get_route_repository),
                         airport_repo: AirportRepository = Depends(get_airport_repository)
) -> CustomerService:
    return CustomerService(airport_repository= airport_repo, route_repository= route_repo, flight_repository= flight_repo)

@app.get("/status")
def basic_return():
    return {"Status": "Ok!"}
# Customer endpoints
@app.get("/customer/active_flights", response_model=list[Flight])
def get_customer_flights_per_city(
    origin_city: str,
    svc: CustomerService
):
    return svc.scheduled_flights_by_city(origin_city)


#
#
# Customer Endpoints
#
#
@app.get("/customer/airport_info")
def airport_information_by_flight(
    flight: Flight,
    srv: CustomerService = Depends(get_customer_service)
):
    return srv.airport_information_by_flight(flight)

#
#
# HR EMPLOYEE ENDPOINTS
#
#
# Repository Getter
def get_in_flight_employee_repository(db: Session = Depends(get_db)) -> InFlightEmployeeRepository:
    return InFlightEmployeeRepository(db)

# Service Getter
def get_in_flight_employee_service(repo: InFlightEmployeeRepository = Depends(get_in_flight_employee_repository)) -> InFlightEmployeeService:
    return InFlightEmployeeService(repo)



@app.get("/hr/employees", response_model=list[InFlightEmployee])
def track_employee_positions(
    position: EmployeePosition = Query(None, description="Filter by position"),
    status: str = Query(None, description="Filter by status"),
    svc: InFlightEmployeeService = Depends(get_in_flight_employee_service)
):
    """Track employee positions and statuses for compliance"""
    employees = svc.listall()
    
    if position:
        employees = [e for e in employees if e.position.value == position.value]
    if status:
        employees = [e for e in employees if str(e.status) == status]
    
    return employees



@app.delete("/hr/employees/{employee_id}")
def remove_past_employee(
    employee_id: UUID,
    svc: InFlightEmployeeService = Depends(get_in_flight_employee_service)
):
    """Remove past employees from the system"""
    employee = svc.get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    svc.delete(employee_id)
    return {"status": "success", "message": f"Employee {employee_id} removed successfully"}
#
#
# Employee Endpoints
#
#

#
#
# Aircraft Scheduler Endpoints
#
#

# As a scheduler, I want to assign aircraft to flights based on availability and route requirements
#@app.post("/scheduler/assign_aircraft")
#def assign_aircraft_to_flight(srv):
    # 
#
#
# Operations Manager Endpoints
#
#


# /user/active_flights

# /dispatcher/scheduled_per_rouute

# /cs_agent/route_details

# /crew_member/scheduled_flights

# repo structure
# one service layer method - calls whatever repos it needs
#   lots of repo files
# 



# - - - - - - CRUD endpoints - - - - - -

# GET, POST, PATCH, PUT, DELETE
# "/user/flight"
#@app.get("/user/flight")
#def get_flight(svc: ):
    
    

# GET, POST, PATCH, PUT, DELETE
# "/user/aircraft"

# GET, POST, PATCH, PUT, DELETE
# "/user/flight-crew"

# GET, POST, PATCH, PUT, DELETE
# "/user/route"

# GET, POST, PATCH, PUT, DELETE
# "/user/in-flight-employee"

