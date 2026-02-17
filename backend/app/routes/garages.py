"""Garage endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models import Garage

router = APIRouter()


class GarageCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None
    address: str | None = None
    postcode: str | None = None


@router.get("/")
async def get_garages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Garage))
    return result.scalars().all()


@router.post("/")
async def create_garage(data: GarageCreate, db: AsyncSession = Depends(get_db)):
    garage = Garage(**data.model_dump())
    db.add(garage)
    await db.commit()
    await db.refresh(garage)
    return garage
