from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models import Barber, Shop

class BarberRepository:

    @staticmethod
    async def get_shop_by_id(db: AsyncSession, shop_id: int):
        result = await db.execute(select(Shop).filter(Shop.shop_id == shop_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_barber_by_id(db: AsyncSession, barber_id: int):
        result = await db.execute(select(Barber).filter(Barber.barber_id == barber_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_available_barbers(db: AsyncSession, shop_id: int):
        result = await db.execute(
            select(Barber).filter(Barber.shop_id == shop_id, Barber.is_available == True)
        )
        return result.scalars().all()

    @staticmethod
    async def add_barber(db: AsyncSession, barber: Barber):
        db.add(barber)
        await db.commit()
        await db.refresh(barber)
        return barber

    @staticmethod
    async def delete_barber(db: AsyncSession, barber: Barber):
        await db.delete(barber)
        await db.commit()

    @staticmethod
    async def update_barber(db: AsyncSession, barber: Barber):
        await db.commit()
        await db.refresh(barber)
        return barber
