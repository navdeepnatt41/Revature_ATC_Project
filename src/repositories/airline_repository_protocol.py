from typing import Protocol, Optional
from src.domain.airline import Airline

class AirlineRepositoryProtocol(Protocol):
    def create(self, airline: Airline) -> Airline:
        ...

    def get(self, airline_designator: str) -> Optional[Airline]:
        ...

    def list_all(self) -> list[Airline]:
        ...

    def update(self, airline: Airline) -> Airline:
        ...

    def delete(self, airline_designator: str) -> None:
        ...