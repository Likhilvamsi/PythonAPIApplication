from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.schemas.barber_schemas import BarberCreate, BarberUpdate
from src.services.barber_service import BarberService

router = APIRouter(prefix="/barbers", tags=["Barbers"])

@router.post("/add/{shop_id}")
async def add_barber(shop_id: int, barber: BarberCreate, db: AsyncSession = Depends(get_db)):
    return await BarberService.add_barber(db, shop_id, barber)

@router.put("/update/{barber_id}")
async def update_barber(barber_id: int, owner_id: int, barber: BarberUpdate, db: AsyncSession = Depends(get_db)):
    return await BarberService.update_barber(db, barber_id, owner_id, barber)

@router.delete("/delete/{barber_id}")
async def delete_barber(barber_id: int, owner_id: int, db: AsyncSession = Depends(get_db)):
    return await BarberService.delete_barber(db, barber_id, owner_id)

@router.get("/available/{shop_id}")
async def get_available_barbers(shop_id: int, db: AsyncSession = Depends(get_db)):
    return await BarberService.get_available_barbers(db, shop_id)
