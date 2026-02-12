from typing import Optional
from sqlalchemy.orm import Session
from src.repositories.operates_repository_protocol import OperatesRepositoryProtocol
from src.domain.operates import Operates

class OperatesRepository(OperatesRepositoryProtocol):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, operate: Operates) -> Operates:
        self.session.add(operate)
        self.session.commit()
        self.session.refresh(operate)
        return operate
    
    def get(self, airport_code: str, airline_designator: str) -> Optional[Operates]:
        return (
            self.session.query(Operates)
            .filter(
                Operates.airport_code == airport_code,
                Operates.airline_designator == airline_designator
            )
            .one_or_none()
        )

    def list_all(self) -> list[Operates]:
        return self.session.query(Operates).all()

    def update(self, operate: Operates) -> Operates:
        existing = self.session.get(
            Operates,
            (operate.airport_code, operate.airline_designator)
        )
        if existing is None:
            raise ValueError("Operates record not found")

        self.session.commit()
        self.session.refresh(existing)
        return existing

    def delete(self, airport_code: str, airline_designator: str) -> None:
        operate = self.session.get(
            Operates,
            (airport_code, airline_designator)
        )
        if operate is None:
            raise ValueError("Operates record not found")
        self.session.delete(operate)
        self.session.commit()