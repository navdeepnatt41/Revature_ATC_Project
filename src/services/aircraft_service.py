from uuid import UUID

from src.domain.aircraft import Aircraft, AircraftStatus
from src.domain.exceptions import (
    AppErrorException,
    EntityAlreadyExistsException,
    NotFoundException,
    PermissionDeniedException,
)

from src.repositories.aircraft_repository_protocol import AircraftRepositoryProtocol
from src.repositories.airport_repository_protocol import AirportRepositoryProtocol


class AircraftService:
    def __init__(
        self,
        aircraft_repo: AircraftRepositoryProtocol,
        airport_repo: AirportRepositoryProtocol,
    ):
        self.aircraft_repo = aircraft_repo
        self.airport_repo = airport_repo

    def repair_aircraft(self, aircraft_id: UUID) -> Aircraft:
        aircraft = self.aircraft_repo.get(aircraft_id)
        if aircraft.aircraft_status == AircraftStatus.AOG:
            aircraft.aircraft_status = AircraftStatus.AVAILABLE
            aircraft.current_distance = 0
            self.aircraft_repo.update(aircraft)
        return aircraft

    def decommission_aircraft(self, aircraft_id: UUID):
        aircraft = self.aircraft_repo.get(aircraft_id)
        if aircraft is None:
            raise NotFoundException("aircraft cannot be found")
        if aircraft.aircraft_status != AircraftStatus.AVAILABLE:
            raise AppErrorException(f"Cannot decommission aircraft in use")
        self.aircraft_repo.delete(aircraft_id)

    def available_aircraft_at_airport(self, airport_code: str) -> list[Aircraft]:
        return self.aircraft_repo.available_aircraft_by_airport(airport_code)

