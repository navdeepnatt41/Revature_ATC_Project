"""
SQLAlchemy ORM object for an Airport
"""

from dataclasses import dataclass

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.base import Base


@dataclass
class Airport(Base):
    """
    The Airport ORM for the Airport table in the database.

    Attributes:
        airport_code (Column[String]): The IANA code that uniquely identifies an airport
        airport_name (Column[String]): The official name for an airport
        airport_country (Column[String]): The country in which the airport is located
        airport_city (Column[String]): The city in which the airport is located
        airport_address (Column[String]): The official address of an airport
        longitude (Column[String]): The longitude co-ordinate point of the airport
        latitutde (Column[String]): The latitutde co-ordinate point of the airport
    """

    __tablename__ = "airport"

    airport_code: Mapped[str] = mapped_column(String, primary_key=True)
    airport_name: Mapped[str] = mapped_column(String)
    airport_country: Mapped[str] = mapped_column(String)
    airport_city: Mapped[str] = mapped_column(String)
    airport_address: Mapped[str] = mapped_column(String)
    longitude: Mapped[str] = mapped_column(String)
    latitude: Mapped[str] = mapped_column(String)
