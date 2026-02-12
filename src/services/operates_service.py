from typing import Optional
from src.domain.operates import Operates
from src.repositories.operates_repository_protocol import OperatesRepositoryProtocol


class OperatesService:
    def __init__(self, repo: OperatesRepositoryProtocol):
        self.repo = repo

    def create(self, operate: Operates) -> Operates:
        self._validate_operate(operate)
        return self.repo.create(operate)

    def get(self, airport_code: str, airline_designator: str) -> Optional[Operates]:
        return self.repo.get(airport_code, airline_designator)

    def list_all(self) -> list[Operates]:
        return self.repo.list_all()

    def update(self, operate: Operates) -> Operates:
        self._validate_operate(operate)
        return self.repo.update(operate)

    def delete(self, airport_code: str, airline_designator: str) -> None:
        self.repo.delete(airport_code, airline_designator)

    def _validate_operate(self, operate: Operates) -> None:
        if not operate.airport_code:
            raise ValueError("airport_code is required")
        if not operate.airline_designator:
            raise ValueError("airline_designator is required")