from typing import Optional
from uuid import UUID

from src.repositories.flight_repository_protocol import FlightRepositoryProtocol

from src.domain.flight import Flight
from src.domain.flight import FlightStatus


class OperationsManagerService:
    def __init__(self,
                 flight_repository: FlightRepositoryProtocol
                 ):
        self.flight_repository = flight_repository

    def update_flight_status_by_id(self,
        flight_id : UUID,
        new_status: FlightStatus,
        ):

        flight = self.flight_repository.get(flight_id)
        if flight is None:
            raise ValueError("Flight not found")
        
        flight.flight_status = new_status
        
        return self.flight_repository.update(flight)
    
    
