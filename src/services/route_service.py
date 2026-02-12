from typing import Optional
from uuid import UUID
from src.domain.route import Route
from src.repositories.route_repository_protocol import RouteRepositoryProtocol


class RouteService:
    def __init__(self, repo: RouteRepositoryProtocol):
        self.repo = repo

    def create(self, route: Route) -> Route:
        self._validate_route(route, require_id=False)
        return self.repo.create(route)

    def get(self, route_id: UUID) -> Optional[Route]:
        return self.repo.get(route_id)

    def list_all(self) -> list[Route]:
        return self.repo.list_all()

    def update(self, route: Route) -> Route:
        self._validate_route(route, require_id=True)
        return self.repo.update(route)

    def delete(self, route_id: UUID) -> None:
        self.repo.delete(route_id)

    def _validate_route(self, route: Route, require_id: bool) -> None:
        if require_id and not route.route_id:
            raise ValueError("route_id is required for update")
        if not route.origin_airport_code:
            raise ValueError("origin_airport_code is required")
        if not route.destination_airport_code:
            raise ValueError("destination_airport_code is required")
        if route.origin_airport_code == route.destination_airport_code:
            raise ValueError("origin and destination airports must be different")