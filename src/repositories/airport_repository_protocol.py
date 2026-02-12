from typing import Protocol, Optional
from src.domain.airport import Airport

class AirportRepositoryProtocol(Protocol):
    def create(self, airport: Airport) -> Airport:
        ...

    def get(self, airport_code: str) -> Optional[Airport]:
        ...

    def list_all(self) -> list[Airport]:
        ...

    def update(self, airport: Airport) -> Airport:
        ...

    def delete(self, airport_code: str) -> None:
        ...