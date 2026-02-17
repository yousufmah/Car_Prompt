from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Garage(Base):
    __tablename__ = "garages"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    address = Column(Text)
    postcode = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)

    listings = relationship("CarListing", back_populates="garage")


class CarListing(Base):
    __tablename__ = "car_listings"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    make = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    variant = Column(String(100))
    year = Column(Integer, nullable=False, index=True)
    price = Column(Float, nullable=False, index=True)
    mileage = Column(Integer)
    fuel_type = Column(String(50), index=True)
    transmission = Column(String(50), index=True)
    body_type = Column(String(50), index=True)
    doors = Column(Integer)
    colour = Column(String(50))
    engine_size = Column(Float)
    location = Column(String(100))
    postcode = Column(String(10))
    images = Column(Text)  # JSON array of URLs
    garage_id = Column(Integer, ForeignKey("garages.id"))
    embedding = Column(Vector(1536))  # OpenAI ada-002 embeddings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    garage = relationship("Garage", back_populates="listings")


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True)
    user_prompt = Column(Text, nullable=False)
    parsed_filters = Column(Text)  # JSON
    results_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
