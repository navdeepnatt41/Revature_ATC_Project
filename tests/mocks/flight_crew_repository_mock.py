from typing import Optional
from uuid import UUID
from src.domain.flight_crew import FlightCrew


class MockFlightCrewRepository:
    def create(self, flight_crew: FlightCrew) -> FlightCrew:
        return flight_crew

    def get(self, flight_id: UUID, employee_id: UUID) -> Optional[FlightCrew]:
        return FlightCrew(flight_id, employee_id)

    def get_by_flight(self, flight_id: UUID) -> list[FlightCrew]:
        return [
            FlightCrew(flight_id, employee_id = 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1'),
            FlightCrew(flight_id, employee_id = 'aaaaaaa2-aaaa-aaaa-aaaa-aaaaaaaaaaa2')
        ]

    def list_all(self) -> list[FlightCrew]:
        return [
            FlightCrew(flight_id = 'f1111111-1111-1111-1111-111111111111', employee_id = 'aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1'),
            FlightCrew(flight_id = 'f2222222-2222-2222-2222-222222222222', employee_id = 'aaaaaaa2-aaaa-aaaa-aaaa-aaaaaaaaaaa2')
        ]

    def update(self, flight_crew: FlightCrew) -> FlightCrew:
        return flight_crew
    
    def delete(self, flight_id: UUID, employee_id: UUID) -> None:
        pass
        