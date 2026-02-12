from src.repositories.airport_repository_protocol import AirportRepositoryProtocol
from src.repositories.route_protocol import RouteRepositoryProtocol
from src.repositories.flight_repository_protocol import FlightRepositoryProtocol
from src.repositories.in_flight_employee_repository_protocol import InFlightEmployeeRepositoryProtocol
from src.repositories.flight_crew_repository_protocol import FlightCrewRepositoryProtocol



from src.domain.airport import Airport
from src.domain.route import Route
from src.domain.flight import Flight
from src.domain.in_flight_employee import InFlightEmployee

from typing import Optional

class HRemployeeService:
    def __init__(
            self,
            airport_repository : AirportRepositoryProtocol,
            route_repository : RouteRepositoryProtocol,
            flight_repository : FlightRepositoryProtocol,
            in_flight_crew_repository : InFlightEmployeeRepositoryProtocol,
    ):
        self.airport_repository = airport_repository
        self.route_repository = route_repository
        self.flight_repository = flight_repository
        self.in_flight_crew_repository = in_flight_crew_repository

    def get_employee_by_names(
            self,
            first_name: str = None,
            last_name: Optional[str] = None,
    ):
        if first_name:
            return self.in_flight_crew_repository.find_by_first(first_name)
        elif first_name and last_name:
            return self.in_flight_crew_repository.find_by_first_and_last(first_name,last_name)
        
        raise ValueError("Error: first_name, last_name, or both missing")
    


