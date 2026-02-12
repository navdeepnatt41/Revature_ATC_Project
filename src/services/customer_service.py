from uuid import UUID

from src.repositories.airport_repository_protocol import AirportRepositoryProtocol
from src.repositories.route_protocol import RouteRepositoryProtocol
from src.repositories.flight_repository_protocol import FlightRepositoryProtocol

from src.domain.airport import Airport
from src.domain.route import Route
from src.domain.flight import Flight
from src.domain.flight import FlightStatus

class CustomerService:
    def __init__(self, airport_repository: AirportRepositoryProtocol, 
                 route_repository: RouteRepositoryProtocol,
                 flight_repository: FlightRepositoryProtocol
    ):
        self.airport_repository = airport_repository
        self.route_repository = route_repository
        self.flight_repository = flight_repository

    def airport_information_by_flight(self, flight: Flight) -> tuple[Airport, Airport] | None:
        route = self.route_repository.get(UUID(str(flight.route_id)))
        if route:
            origin = self.airport_repository.get(str(route.destination_airport_code))
            destination = self.airport_repository.get(str(route.destination_airport_code))  
            return (origin, destination)

    def scheduled_flights_by_city(self, city: str) -> list[Flight]:
        return self.flight_repository.get_scheduled_by_city(city)