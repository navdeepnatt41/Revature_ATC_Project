"""
Defines the Route ORM model
"""
import uuid
from math import asin, cos, radians, sin, sqrt
from dataclasses import dataclass

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from src.base import Base


@dataclass
class Route(Base):
    """
    Route is an ORM model for the Route table in the database. It defines the routes that the airline flies.
    
    Attributes:
        route_id (UUID): The UUID of the route. We may want to change this to
                        simply be the concatenation of destination and
                        origin.
        destination_airport_code (str): The IATA code of the destination airport of this route.
        origin_airport_code (str): The IATA code of the origin airport of this route.
    """
    __tablename__ = "route"

    route_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_airport_code: Mapped[str] = mapped_column(
        String, ForeignKey("airport.airport_code"), nullable=False
    )
    origin_airport_code: Mapped[str] = mapped_column(
        String, ForeignKey("airport.airport_code"), nullable=False
    )
