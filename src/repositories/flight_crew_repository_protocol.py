from typing import Protocol, Optional
from uuid import UUID
from src.domain.flight_crew import FlightCrew

class FlightCrewRepositoryProtocol(Protocol):
    def create(self, flight_crew: FlightCrew) -> FlightCrew:
        ...

    def get(self, flight_id: UUID, employee_id: UUID) -> Optional[FlightCrew]:
        ...

    def get_by_flight(self, flight_id: UUID) -> list[FlightCrew]:
        ...

    def list_all(self) -> list[FlightCrew]:
        ...

    def update(self, flight_crew: FlightCrew) -> FlightCrew:
        ...

    def delete(self, flight_id: UUID, employee_id: UUID) -> None:
        ...