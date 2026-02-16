"""
Data Transfer Objects (DTOs) for Route entities.
"""
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RouteCreate(BaseModel):
    """
    Data schema for creating a new flight route.
    """
    origin_airport_code: str = Field(..., description="IATA code for the starting airport")
    destination_airport_code: str = Field(..., description="IATA code for the target airport")


class RouteRead(BaseModel):
    """
    Data schema for representing a route retrieved from the database.
    """
    route_id: UUID = Field(..., description="Unique database identifier for the route")
    origin_airport_code: str = Field(..., description="IATA code for the starting airport")
    destination_airport_code: str = Field(..., description="IATA code for the target airport")

    model_config = ConfigDict(from_attributes=True)