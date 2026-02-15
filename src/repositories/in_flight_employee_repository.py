from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.domain.airport import Airport
from src.domain.in_flight_employee import InFlightEmployee, InFlightStatus
from src.repositories.in_flight_employee_repository_protocol import (
    InFlightEmployeeRepositoryProtocol,
)


class InFlightEmployeeRepository(InFlightEmployeeRepositoryProtocol):
    def __init__(self, session: Session):
        self.session = session

    def create(self, employee: InFlightEmployee) -> InFlightEmployee:
        self.session.add(employee)
        self.session.commit()
        self.session.refresh(employee)
        return employee

    def get(
        self, employee_id: UUID
    ) -> Optional[InFlightEmployee]:  # returning one employee
        return (
            self.session.query(InFlightEmployee)
            .filter(InFlightEmployee.employee_id == employee_id)
            .one_or_none()  # returning None if none is found
        )

    def find_by_first_and_last(
        self, first: str, last: str
    ) -> Optional[list[InFlightEmployee]]:
        return (
            self.session.query(InFlightEmployee)
            .filter(
                InFlightEmployee.f_name == first.lower(),
                InFlightEmployee.l_name == last.lower(),
            )
            .all()
        )

    def find_by_first(self, first: str) -> list[InFlightEmployee]:
        first = first.strip()
        return (
            self.session.query(InFlightEmployee)
            .filter(InFlightEmployee.f_name == first.lower())
            .all()
        )

    def list_all(self) -> list[InFlightEmployee]:
        return self.session.query(InFlightEmployee).all()

    def update_status_location(
        self, employee: InFlightEmployee, status: InFlightStatus, location: str
    ) -> InFlightEmployee:
        existing = self.session.get(InFlightEmployee, employee.employee_id)
        if existing is None:
            raise ValueError("Employee not found")
        setattr(existing, "employee_status", status)
        setattr(existing, "employee_location", location)

        self.session.commit()
        self.session.refresh(existing)
        return existing

    def delete(self, employee_id: UUID) -> None:
        employee = self.session.get(InFlightEmployee, employee_id)
        if employee is None:
            raise ValueError("Employee not found")
        self.session.delete(employee)
        self.session.commit()

    def available_employees_at_airport(self, airport_code: str) -> list[InFlightEmployee]:
        return (
            self.session.scalars(
                select(InFlightEmployee)
                .where(InFlightEmployee.employee_location == airport_code)
                .where(InFlightEmployee.employee_status == InFlightStatus.AVAILABLE)
            ).all()
        )