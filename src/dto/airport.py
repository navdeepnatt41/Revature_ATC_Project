"""
Data Transfer Objects (DTOs) for Airport entities.
"""
from pydantic import BaseModel, ConfigDict, Field


class AirportBase(BaseModel):
    """
    Base properties for an Airport.
    """
    airport_code: str = Field(
        ..., 
        min_length=3, 
        max_length=4, 
        description="IATA (3-letter) or ICAO (4-letter) airport code"
    )
    airport_name: str = Field(..., description="Full name of the airport facility")
    airport_country: str = Field(..., description="The country where the airport is located")
    airport_city: str = Field(..., description="The primary city served by the airport")
    airport_address: str = Field(..., description="Physical street address of the terminal")
    
    longitude: str = Field(..., description="Geographic longitude coordinate")
    latitude: str = Field(..., description="Geographic latitude coordinate")


class AirportCreate(AirportBase):
    """
    Schema for registering a new airport in the system.
    """
    pass


class AirportRead(AirportBase):
    """
    Schema for airport data retrieved from the database.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "airport_code": "JFK",
                "airport_name": "John F. Kennedy International Airport",
                "airport_country": "USA",
                "airport_city": "New York",
                "airport_address": "Queens, NY 11430",
                "longitude": "-73.7781",
                "latitude": "40.6413"
            }
        }
    )