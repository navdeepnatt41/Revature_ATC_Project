from typing import Optional, Protocol
from uuid import UUID

from src.domain.aircraft import Aircraft
from src.domain.airport import Airport


class AircraftRepositoryProtocol(Protocol):
    def create(self, aircraft: Aircraft) -> Aircraft: ...

    def get(self, aircraft_id: UUID) -> Optional[Aircraft]: ...

    def list_all(self) -> list[Aircraft]: ...

    def update(self, aircraft: Aircraft) -> Aircraft: ...

    def delete(self, aircraft_id: UUID) -> None: ...

    def available_aircraft_by_airport(self, airport_code: str) -> list[Aircraft]: 
        ...
