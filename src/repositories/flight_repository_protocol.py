from typing import Protocol, Optional
from uuid import UUID
from src.domain.flight import Flight

class FlightRepositoryProtocol(Protocol):
    def create(self, flight: Flight) -> Flight:
        ...

    def get(self, flight_id: UUID) -> Optional[Flight]:
        ...

    def list_all(self) -> list[Flight]:
        ...

    def update(self, flight: Flight) -> Flight:
        ...

    def delete(self, flight_id: UUID) -> None:
        ...

    def get_scheduled_by_city(self, origin_city: str) -> list[Flight]:
        ...