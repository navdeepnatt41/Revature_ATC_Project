from typing import Optional
from uuid import UUID
from src.domain.flight_crew import FlightCrew
from src.repositories.flight_crew_repository_protocol import FlightCrewRepositoryProtocol
from sqlalchemy.orm import Session


class FlightCrewRepository(FlightCrewRepositoryProtocol):
    def __init__(self, session: Session):
        self.session = session
        
    def create(self, flight_crew: FlightCrew) -> FlightCrew:
        self.session.add(flight_crew)
        self.session.commit()
        self.session.refresh(flight_crew)
        return flight_crew

    def get(self, flight_id: UUID, employee_id: UUID) -> Optional[FlightCrew]:
        return (
            self.session.query(FlightCrew)
            .filter(FlightCrew.flight_id == flight_id,
                    FlightCrew.employee_id == employee_id
            )
            .one_or_none()
        )

    def list_all(self) -> list[FlightCrew]:
        return self.session.query(FlightCrew).all()

    def update(self, flight_crew: FlightCrew) -> FlightCrew:
        existing = self.session.get(
            FlightCrew,
            (flight_crew.flight_id, flight_crew.employee_id),
        )
        if existing is None:
            raise ValueError("Flight Crew assignment not found")

        return existing
    
    def delete(self, flight_id: UUID, employee_id: UUID) -> None:
        flight_crew = self.session.get(FlightCrew, (flight_id, employee_id))
        if flight_crew is None:
            raise ValueError("Flight Crew assignment not found")
        self.session.delete(flight_crew)
        self.session.commit()
        