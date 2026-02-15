from typing import Optional
from uuid import UUID

from src.domain.flight import Flight
from src.repositories.flight_repository_protocol import FlightRepositoryProtocol
from src.domain.route import Route
from src.domain.airport import Airport


class MockFlightRepository:
    def create(self, flight: Flight) -> Flight:
        return flight

    def get(self, flight_id: UUID) -> Optional[Flight]:
        return Flight(flight_id = flight_id, route_id = 'b1111111-1111-1111-1111-111111111111', flight_status = 'SCHEDULED', aircraft_id = '11111111-1111-1111-1111-111111111111', arrival_time = '2022-03-01 14:00:00', departure_time = '2022-03-01 10:00:00')

    def list_all(self) -> list[Flight]:
        return [
            Flight('f1111111-1111-1111-1111-111111111111', route_id = 'b1111111-1111-1111-1111-111111111111', flight_status = 'SCHEDULED', aircraft_id = '11111111-1111-1111-1111-111111111111', arrival_time = '2022-03-01 14:00:00', departure_time = '2022-03-01 10:00:00'),
            Flight('f2222222-2222-2222-2222-222222222222', route_id = 'b1111111-1111-1111-1111-111111111111', flight_status = 'ARRIVED', aircraft_id = '11111111-1111-1111-1111-111111111111', arrival_time = '2021-03-01 14:00:00', departure_time = '2021-03-01 10:00:00')
        ]

    def update(self, flight: Flight) -> Flight:
        return flight

    def delete(self, flight_id: UUID) -> None:
        pass

    def get_scheduled_by_city(self, origin_city: str) -> list[Flight]:
        return [Flight('f1111111-1111-1111-1111-111111111111', route_id = 'b1111111-1111-1111-1111-111111111111', flight_status = 'SCHEDULED', aircraft_id = '11111111-1111-1111-1111-111111111111', arrival_time = '2022-03-01 14:00:00', departure_time = '2022-03-01 10:00:00')]