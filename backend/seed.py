"""
Seed script — populates the database with mock car listings for development.

Usage:
    python seed.py

Requires DATABASE_URL in .env (or environment).
Does NOT require OpenAI API key — uses zero vectors for embeddings.
"""

import asyncio
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost:5432/carprompt")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

MOCK_GARAGES = [
    {"name": "City Motors Birmingham", "email": "info@citymotors.co.uk", "phone": "0121 000 0001", "address": "123 High Street", "postcode": "B1 1AA"},
    {"name": "Northern Auto Group", "email": "sales@northernauto.co.uk", "phone": "0161 000 0002", "address": "456 Market Street", "postcode": "M1 1BB"},
    {"name": "South Coast Cars", "email": "hello@southcoastcars.co.uk", "phone": "01273 000003", "address": "789 Beach Road", "postcode": "BN1 1CC"},
]

MOCK_LISTINGS = [
    {
        "title": "2019 Toyota Yaris 1.5 VVT-i Icon",
        "description": "Excellent first car. Low insurance group, great fuel economy. Full service history. One careful owner.",
        "make": "toyota", "model": "yaris", "variant": "1.5 VVT-i Icon",
        "year": 2019, "price": 9500, "mileage": 28000,
        "fuel_type": "petrol", "transmission": "manual", "body_type": "hatchback",
        "doors": 5, "colour": "silver", "engine_size": 1.5,
        "location": "Birmingham", "postcode": "B1 1AA", "garage_id": 1,
    },
    {
        "title": "2020 Honda Jazz 1.5 i-MMD Hybrid SR",
        "description": "Incredibly reliable hybrid. Superb fuel economy, spacious interior for its size. Perfect city car.",
        "make": "honda", "model": "jazz", "variant": "1.5 i-MMD Hybrid SR",
        "year": 2020, "price": 14995, "mileage": 19500,
        "fuel_type": "hybrid", "transmission": "automatic", "body_type": "hatchback",
        "doors": 5, "colour": "white", "engine_size": 1.5,
        "location": "Manchester", "postcode": "M1 1BB", "garage_id": 2,
    },
    {
        "title": "2018 Ford Focus 2.0 TDCi ST-Line",
        "description": "Sporty looks with diesel economy. Great motorway cruiser, low running costs.",
        "make": "ford", "model": "focus", "variant": "2.0 TDCi ST-Line",
        "year": 2018, "price": 11750, "mileage": 45000,
        "fuel_type": "diesel", "transmission": "manual", "body_type": "hatchback",
        "doors": 5, "colour": "blue", "engine_size": 2.0,
        "location": "Brighton", "postcode": "BN1 1CC", "garage_id": 3,
    },
    {
        "title": "2021 Volkswagen Golf 1.5 TSI Life",
        "description": "Premium hatchback with all the mod cons. Apple CarPlay, parking sensors, LED lights. Stunning condition.",
        "make": "volkswagen", "model": "golf", "variant": "1.5 TSI Life",
        "year": 2021, "price": 20500, "mileage": 14000,
        "fuel_type": "petrol", "transmission": "automatic", "body_type": "hatchback",
        "doors": 5, "colour": "grey", "engine_size": 1.5,
        "location": "Birmingham", "postcode": "B2 2BB", "garage_id": 1,
    },
    {
        "title": "2017 BMW 3 Series 320d M Sport",
        "description": "Iconic executive saloon. M Sport body kit, leather seats, heads-up display. Drives beautifully.",
        "make": "bmw", "model": "3 series", "variant": "320d M Sport",
        "year": 2017, "price": 16800, "mileage": 58000,
        "fuel_type": "diesel", "transmission": "automatic", "body_type": "saloon",
        "doors": 4, "colour": "black", "engine_size": 2.0,
        "location": "Manchester", "postcode": "M2 2CC", "garage_id": 2,
    },
    {
        "title": "2022 Tesla Model 3 Long Range AWD",
        "description": "358 mile range. Supercharger network access. Autopilot included. Like new — barely used.",
        "make": "tesla", "model": "model 3", "variant": "Long Range AWD",
        "year": 2022, "price": 36900, "mileage": 8500,
        "fuel_type": "electric", "transmission": "automatic", "body_type": "saloon",
        "doors": 4, "colour": "white", "engine_size": None,
        "location": "Brighton", "postcode": "BN2 2DD", "garage_id": 3,
    },
    {
        "title": "2019 Nissan Qashqai 1.5 dCi N-Connecta",
        "description": "The UK's favourite SUV. Panoramic roof, 360° camera, heated seats. Perfect family car.",
        "make": "nissan", "model": "qashqai", "variant": "1.5 dCi N-Connecta",
        "year": 2019, "price": 15500, "mileage": 36000,
        "fuel_type": "diesel", "transmission": "manual", "body_type": "suv",
        "doors": 5, "colour": "red", "engine_size": 1.5,
        "location": "Birmingham", "postcode": "B3 3CC", "garage_id": 1,
    },
    {
        "title": "2020 Volkswagen Tiguan 2.0 TDI 4Motion SEL",
        "description": "4WD family SUV. 7 seats, massive boot, very comfortable. Ideal for families.",
        "make": "volkswagen", "model": "tiguan", "variant": "2.0 TDI 4Motion SEL",
        "year": 2020, "price": 27500, "mileage": 29000,
        "fuel_type": "diesel", "transmission": "automatic", "body_type": "suv",
        "doors": 5, "colour": "grey", "engine_size": 2.0,
        "location": "Manchester", "postcode": "M3 3DD", "garage_id": 2,
    },
    {
        "title": "2016 Mazda MX-5 2.0 Sport Nav",
        "description": "Pure driving joy. Lightweight, rear-wheel drive, razor-sharp handling. Garaged all its life.",
        "make": "mazda", "model": "mx-5", "variant": "2.0 Sport Nav",
        "year": 2016, "price": 13500, "mileage": 41000,
        "fuel_type": "petrol", "transmission": "manual", "body_type": "convertible",
        "doors": 2, "colour": "red", "engine_size": 2.0,
        "location": "Brighton", "postcode": "BN3 3EE", "garage_id": 3,
    },
    {
        "title": "2021 Ford Puma 1.0 EcoBoost ST-Line",
        "description": "Sharp crossover with a sporty edge. Great on fuel, very practical with the MegaBox under the boot floor.",
        "make": "ford", "model": "puma", "variant": "1.0 EcoBoost ST-Line",
        "year": 2021, "price": 18200, "mileage": 17500,
        "fuel_type": "petrol", "transmission": "manual", "body_type": "suv",
        "doors": 5, "colour": "blue", "engine_size": 1.0,
        "location": "Birmingham", "postcode": "B4 4DD", "garage_id": 1,
    },
    {
        "title": "2015 Toyota Prius 1.8 VVT-i Plug-in",
        "description": "Hybrid pioneer. Unbeatable running costs, incredibly reliable. Popular with private hire drivers.",
        "make": "toyota", "model": "prius", "variant": "1.8 VVT-i Plug-in",
        "year": 2015, "price": 8900, "mileage": 72000,
        "fuel_type": "hybrid", "transmission": "automatic", "body_type": "hatchback",
        "doors": 5, "colour": "silver", "engine_size": 1.8,
        "location": "Manchester", "postcode": "M4 4EE", "garage_id": 2,
    },
    {
        "title": "2018 Mercedes-Benz C-Class C220d AMG Line",
        "description": "Premium executive saloon. AMG styling, Burmester sound system, widescreen cockpit. Head-turning spec.",
        "make": "mercedes-benz", "model": "c-class", "variant": "C220d AMG Line",
        "year": 2018, "price": 22900, "mileage": 48000,
        "fuel_type": "diesel", "transmission": "automatic", "body_type": "saloon",
        "doors": 4, "colour": "black", "engine_size": 2.0,
        "location": "Brighton", "postcode": "BN4 4FF", "garage_id": 3,
    },
    {
        "title": "2020 Kia Sportage 1.6 CRDi GT-Line S",
        "description": "Seven-year warranty remaining. Full leather, 360° cameras, ventilated seats. Outstanding value.",
        "make": "kia", "model": "sportage", "variant": "1.6 CRDi GT-Line S",
        "year": 2020, "price": 22000, "mileage": 25000,
        "fuel_type": "diesel", "transmission": "automatic", "body_type": "suv",
        "doors": 5, "colour": "white", "engine_size": 1.6,
        "location": "Birmingham", "postcode": "B5 5EE", "garage_id": 1,
    },
    {
        "title": "2019 Audi A3 Sportback 35 TFSI S Line",
        "description": "Premium compact. Virtual cockpit, Bang & Olufsen sound, sport suspension. Flawless condition.",
        "make": "audi", "model": "a3", "variant": "35 TFSI S Line Sportback",
        "year": 2019, "price": 19500, "mileage": 31000,
        "fuel_type": "petrol", "transmission": "automatic", "body_type": "hatchback",
        "doors": 5, "colour": "grey", "engine_size": 1.5,
        "location": "Manchester", "postcode": "M5 5FF", "garage_id": 2,
    },
    {
        "title": "2016 Vauxhall Astra 1.4T SRI",
        "description": "Practical and affordable. Low tax, cheap to insure, decent power. Ideal budget daily driver.",
        "make": "vauxhall", "model": "astra", "variant": "1.4T SRI",
        "year": 2016, "price": 6200, "mileage": 68000,
        "fuel_type": "petrol", "transmission": "manual", "body_type": "hatchback",
        "doors": 5, "colour": "blue", "engine_size": 1.4,
        "location": "Brighton", "postcode": "BN5 5GG", "garage_id": 3,
    },
    {
        "title": "2022 Hyundai Ioniq 5 77kWh Ultimate",
        "description": "Next-gen EV. Ultra-fast 800V charging (10-80% in 18 mins), stunning interior, 302 mile range.",
        "make": "hyundai", "model": "ioniq 5", "variant": "77kWh Ultimate",
        "year": 2022, "price": 39500, "mileage": 11000,
        "fuel_type": "electric", "transmission": "automatic", "body_type": "suv",
        "doors": 5, "colour": "white", "engine_size": None,
        "location": "Birmingham", "postcode": "B6 6FF", "garage_id": 1,
    },
    {
        "title": "2017 Subaru Impreza 2.0i Sport AWD",
        "description": "All-wheel drive, legendary reliability. Japanese quality at its best. Full service history.",
        "make": "subaru", "model": "impreza", "variant": "2.0i Sport AWD",
        "year": 2017, "price": 10500, "mileage": 52000,
        "fuel_type": "petrol", "transmission": "manual", "body_type": "hatchback",
        "doors": 5, "colour": "blue", "engine_size": 2.0,
        "location": "Manchester", "postcode": "M6 6GG", "garage_id": 2,
    },
    {
        "title": "2014 Honda Civic 1.6 i-DTEC SE",
        "description": "Legendary reliability. 78mpg real-world, cheap tax, spacious cabin. Great long-distance car.",
        "make": "honda", "model": "civic", "variant": "1.6 i-DTEC SE",
        "year": 2014, "price": 5800, "mileage": 88000,
        "fuel_type": "diesel", "transmission": "manual", "body_type": "hatchback",
        "doors": 5, "colour": "silver", "engine_size": 1.6,
        "location": "Brighton", "postcode": "BN6 6HH", "garage_id": 3,
    },
    {
        "title": "2021 Toyota RAV4 2.5 PHEV Dynamic Force AWD",
        "description": "Plug-in hybrid SUV. Electric-only mode, 4WD, massive kit list. Perfect family adventurer.",
        "make": "toyota", "model": "rav4", "variant": "2.5 PHEV Dynamic Force AWD",
        "year": 2021, "price": 35000, "mileage": 18000,
        "fuel_type": "hybrid", "transmission": "automatic", "body_type": "suv",
        "doors": 5, "colour": "green", "engine_size": 2.5,
        "location": "Birmingham", "postcode": "B7 7GG", "garage_id": 1,
    },
    {
        "title": "2019 SEAT Leon 1.5 TSI EVO FR",
        "description": "Sporty but practical hatch. FR styling, digital cockpit, full LED. Great driver's car on a budget.",
        "make": "seat", "model": "leon", "variant": "1.5 TSI EVO FR",
        "year": 2019, "price": 13200, "mileage": 33000,
        "fuel_type": "petrol", "transmission": "manual", "body_type": "hatchback",
        "doors": 5, "colour": "red", "engine_size": 1.5,
        "location": "Manchester", "postcode": "M7 7HH", "garage_id": 2,
    },
]


async def seed():
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # Create tables
        from app.models import Base
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Check if already seeded
        from sqlalchemy import select
        from app.models import Garage, CarListing

        existing = await session.execute(select(Garage).limit(1))
        if existing.scalar_one_or_none():
            print("✅ Database already seeded. Skipping.")
            return

        # Insert garages
        print("🏪 Seeding garages...")
        garages = []
        for g in MOCK_GARAGES:
            garage = Garage(**g)
            session.add(garage)
            garages.append(garage)
        await session.flush()

        # Insert listings (with zero vector — real embeddings need OpenAI key)
        print("🚗 Seeding car listings...")
        zero_vector = [0.0] * 1536

        for data in MOCK_LISTINGS:
            listing = CarListing(
                **data,
                embedding=zero_vector,
                images=json.dumps([]),
            )
            session.add(listing)

        await session.commit()
        print(f"✅ Done! Inserted {len(MOCK_GARAGES)} garages and {len(MOCK_LISTINGS)} listings.")
        print("\nYou can now run the API and test searches.")
        print("Note: Semantic (vector) search won't work without real embeddings,")
        print("but filter-based search (make, price, fuel type, etc.) works fine.")


if __name__ == "__main__":
    asyncio.run(seed())
