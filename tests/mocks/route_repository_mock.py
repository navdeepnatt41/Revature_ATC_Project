from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.repositories.route_repository_protocol import RouteRepositoryProtocol
from src.domain.route import Route

class RouteRepository(RouteRepositoryProtocol):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, route: Route) -> Route:
        self.session.add(route)
        self.session.commit()
        self.session.refresh(route)
        return route
    
    def get(self, route_id: UUID) -> Optional[Route]:
        return self.session.get(Route, route_id)

    def list_all(self) -> list[Route]:
        return self.session.query(Route).all()

    def update(self, route: Route) -> Route:
        existing = self.session.get(Route, route.route_id)
        if existing is None:
            raise ValueError("Route not found")

        existing.destination_airport_code = route.destination_airport_code
        existing.origin_airport_code = route.origin_airport_code
        
        self.session.commit()
        self.session.refresh(existing)
        return existing

    def delete(self, route_id: UUID) -> None:
        route = self.session.get(Route, route_id)
        if route is None:
            raise ValueError("Route not found")
        self.session.delete(route)
        self.session.commit()