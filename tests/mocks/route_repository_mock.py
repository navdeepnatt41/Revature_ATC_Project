from typing import Optional
from uuid import UUID
from src.domain.route import Route

class MockRouteRepository:
    def create(self, route: Route) -> Route:
        return route
    
    def get(self, route_id: UUID) -> Optional[Route]:
        return Route(route_id = route_id, origin_airport_code = 'JFK', destination_airport_code = 'JFK')

    def list_all(self) -> list[Route]:
        return [
            Route(route_id = 'b1111111-1111-1111-1111-111111111111', origin_airport_code = 'JFK', destination_airport_code = 'LAX'),
            Route(route_id = 'b2222222-2222-2222-2222-222222222222', origin_airport_code = 'LAX', destination_airport_code = 'JFK')
        ]

    def update(self, route: Route) -> Route:
        return route

    def delete(self, route_id: UUID) -> None:
        pass