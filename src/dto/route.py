from uuid import UUID
from pydantic import BaseModel


class RouteCreate(BaseModel):
    origin_airport_code: str
    destination_airport_code: str


class RouteRead(BaseModel):
    route_id: UUID
    origin_airport_code: str
    destination_airport_code: str

    model_config = {"from_attributes": True}