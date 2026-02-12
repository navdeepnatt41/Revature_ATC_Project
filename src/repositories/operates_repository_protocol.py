from typing import Protocol, Optional
from src.domain.operates import Operates

class OperatesRepositoryProtocol(Protocol):
    def create(self, operate: Operates) -> Operates:
        ...

    def get(self, airport_code: str, airline_designator: str) -> Optional[Operates]:
        ...
    

    def list_all(self) -> list[Operates]:
        ...

    def update(self, operate: Operates) -> Operates:
        ...

    def delete(self, airport_code: str, airline_designator: str) -> None:
        ...