from typing import Protocol, Optional
from uuid import UUID
from src.domain.in_flight_employee import InFlightEmployee

class InFlightEmployeeRepositoryProtocol(Protocol):
    # class InFlightEmployeeRepositoryProtocol
    def create(self, employee: InFlightEmployee) -> InFlightEmployee:
        ...

    def get(self, employee_id: UUID) -> Optional[InFlightEmployee]:
        ...

    def find_by_first_and_last(self, first: str, last: str) -> Optional[InFlightEmployee]:
        ...

    def find_by_first(self, first: str) -> list[InFlightEmployee]:
        ...

    def list_all(self) -> list[InFlightEmployee]:
        ...

    def update(self, employee: InFlightEmployee) -> InFlightEmployee:
        ...

    def delete(self, employee_id: UUID) -> None:
        ...