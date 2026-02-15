from pydantic import BaseModel


class AirportCreate(BaseModel):
    airport_code: str
    airport_name: str
    airport_country: str
    airport_city: str
    airport_address: str
    longitude: str
    latitude: str


class AirportRead(BaseModel):
    airport_code: str
    airport_name: str
    airport_country: str
    airport_city: str
    airport_address: str
    longitude: str
    latitude: str

    model_config = {"from_attributes": True}