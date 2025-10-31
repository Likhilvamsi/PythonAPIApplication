from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Barber
from src.repositories.barber_repo import BarberRepository
from src.schemas.barber_schemas import BarberCreate, BarberUpdate

class BarberService:

    @staticmethod
    async def add_barber(db: AsyncSession, shop_id: int, data: BarberCreate):
        shop = await BarberRepository.get_shop_by_id(db, shop_id)
        if not shop:
            raise HTTPException(status_code=404, detail=f"Shop with id {shop_id} not found")

        barber = Barber(
            barber_name=data.barber_name,
            shop_id=shop_id,
            start_time=data.start_time,
            end_time=data.end_time,
            is_available=data.is_available,
            generate_daily=data.everyday
        )

        await BarberRepository.add_barber(db, barber)
        return {"msg": "Barber added successfully", "barber_id": barber.barber_id}

    @staticmethod
    async def update_barber(db: AsyncSession, barber_id: int, owner_id: int, data: BarberUpdate):
        barber = await BarberRepository.get_barber_by_id(db, barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")

        shop = await BarberRepository.get_shop_by_id(db, barber.shop_id)
        if shop.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this barber")

        barber.barber_name = data.barber_name or barber.barber_name
        barber.start_time = data.start_time or barber.start_time
        barber.end_time = data.end_time or barber.end_time
        barber.is_available = data.is_available if data.is_available is not None else barber.is_available
        barber.generate_daily = data.everyday if data.everyday is not None else barber.generate_daily

        await BarberRepository.update_barber(db, barber)
        return {"msg": "Barber updated successfully", "barber_id": barber.barber_id}

    @staticmethod
    async def delete_barber(db: AsyncSession, barber_id: int, owner_id: int):
        barber = await BarberRepository.get_barber_by_id(db, barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")

        shop = await BarberRepository.get_shop_by_id(db, barber.shop_id)
        if shop.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this barber")

        await BarberRepository.delete_barber(db, barber)
        return {"msg": "Barber deleted successfully"}

    @staticmethod
    async def get_available_barbers(db: AsyncSession, shop_id: int):
        barbers = await BarberRepository.get_available_barbers(db, shop_id)
        if not barbers:
            raise HTTPException(status_code=404, detail="No available barbers found")
        return barbers
