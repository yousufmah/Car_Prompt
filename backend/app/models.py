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


class ImpressionLog(Base):
    __tablename__ = "impression_logs"

    id = Column(Integer, primary_key=True)
    garage_id = Column(Integer, ForeignKey("garages.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("car_listings.id"))
    search_id = Column(Integer, ForeignKey("search_logs.id"))
    position = Column(Integer)  # Position in search results (1-indexed)
    created_at = Column(DateTime, default=datetime.utcnow)

    garage = relationship("Garage")
    listing = relationship("CarListing")
    search = relationship("SearchLog")


class ViewLog(Base):
    __tablename__ = "view_logs"

    id = Column(Integer, primary_key=True)
    garage_id = Column(Integer, ForeignKey("garages.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("car_listings.id"), nullable=False)
    user_session = Column(String(255))  # Optional session identifier
    created_at = Column(DateTime, default=datetime.utcnow)

    garage = relationship("Garage")
    listing = relationship("CarListing")


class LeadLog(Base):
    __tablename__ = "lead_logs"

    id = Column(Integer, primary_key=True)
    garage_id = Column(Integer, ForeignKey("garages.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("car_listings.id"), nullable=False)
    user_session = Column(String(255))
    contact_method = Column(String(50))  # e.g., "phone", "email", "form"
    created_at = Column(DateTime, default=datetime.utcnow)

    garage = relationship("Garage")
    listing = relationship("CarListing")
