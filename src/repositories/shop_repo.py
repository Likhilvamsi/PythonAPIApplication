from sqlalchemy.future import select
from fastapi import HTTPException
from src.db.models import Shop, Barber, BarberSlot, Booking, User
from src.core.logger import logger

class ShopRepository:

    @staticmethod
    async def get_all_shops(db):
        logger.info("Fetching all shops from DB")
        result = await db.execute(select(Shop))
        shops = result.scalars().all()
        if not shops:
            raise HTTPException(status_code=404, detail="No shops found")
        return shops

    @staticmethod
    async def get_shops_by_owner(db, owner_id: int):
        logger.info(f"Fetching shops for owner_id={owner_id}")
        result = await db.execute(select(Shop).filter(Shop.owner_id == owner_id))
        shops = result.scalars().all()
        if not shops:
            raise HTTPException(status_code=404, detail="No shops found for owner")
        return shops

    @staticmethod
    async def get_available_slots(db, shop_id: int, date: str):
        logger.info(f"Fetching available slots for shop_id={shop_id} on date={date}")
        query = (
            select(BarberSlot.slot_id, Barber.barber_id, Barber.barber_name,
                   BarberSlot.slot_time, BarberSlot.status)
            .join(Barber, BarberSlot.barber_id == Barber.barber_id)
            .filter(BarberSlot.shop_id == shop_id, BarberSlot.slot_date == date)
            .order_by(Barber.barber_id, BarberSlot.slot_time)
        )
        result = await db.execute(query)
        slots = result.all()
        if not slots:
            raise HTTPException(status_code=404, detail="No available slots found")
        return slots

    @staticmethod
    async def get_user_by_id(db, user_id: int):
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_existing_shop(db, owner_id: int, shop_name: str):
        result = await db.execute(select(Shop).filter(Shop.owner_id == owner_id, Shop.shop_name == shop_name))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_shop(db, shop_obj):
        logger.info(f"Creating shop: {shop_obj.shop_name}")
        db.add(shop_obj)
        await db.commit()
        await db.refresh(shop_obj)
        return shop_obj

    @staticmethod
    async def get_slot_by_id(db, slot_id: int, shop_id: int):
        result = await db.execute(select(BarberSlot).filter(BarberSlot.slot_id == slot_id, BarberSlot.shop_id == shop_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_booking(db, booking):
        logger.info(f"Creating booking for user_id={booking.user_id}")
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking
