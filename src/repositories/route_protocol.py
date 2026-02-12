from typing import Protocol, Optional
from uuid import UUID
from src.domain.route import Route

class RouteRepositoryProtocol(Protocol):
    def create(self, route: Route) -> Route:
        ...

    def get(self, route_id: UUID) -> Optional[Route]:
        ...

    def list_all(self) -> list[Route]:
        ...

    def update(self, route: Route) -> Route:
        ...

    def delete(self, route_id: UUID) -> None:
        ...