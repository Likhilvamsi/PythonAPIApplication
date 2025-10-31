from fastapi import HTTPException
from src.db.models import Shop, Booking
from src.repositories.shop_repo import ShopRepository
from src.core.logger import logger

class ShopService:

    @staticmethod
    async def get_shops_for_user(db):
        shops = await ShopRepository.get_all_shops(db)
        return [
            {
                "shop_id": s.shop_id,
                "shop_name": s.shop_name,
                "address": s.address,
                "city": s.city,
                "state": s.state,
                "open_time": str(s.open_time),
                "close_time": str(s.close_time),
                "is_open": s.is_open,
            } for s in shops
        ]

    @staticmethod
    async def get_shops_by_owner(db, owner_id: int):
        shops = await ShopRepository.get_shops_by_owner(db, owner_id)
        return [
            {
                "shop_id": s.shop_id,
                "shop_name": s.shop_name,
                "address": s.address,
                "city": s.city,
                "state": s.state,
                "open_time": str(s.open_time),
                "close_time": str(s.close_time),
                "is_open": s.is_open,
            } for s in shops
        ]

    @staticmethod
    async def get_available_slots(db, shop_id: int, date: str):
        slots = await ShopRepository.get_available_slots(db, shop_id, date)
        return [
            {
                "slot_id": r.slot_id,
                "barber_id": r.barber_id,
                "barber_name": r.barber_name,
                "slot_time": str(r.slot_time),
                "status": r.status
            }
            for r in slots
        ]

    @staticmethod
    async def create_shop_if_not_exists(db, owner_id, shop_data):
        user = await ShopRepository.get_user_by_id(db, owner_id)
        if not user:
            raise HTTPException(status_code=404, detail="Owner not found")

        if user.role not in ["owner", "shop_owner"]:
            raise HTTPException(status_code=403, detail="User not authorized to create shop")

        existing = await ShopRepository.get_existing_shop(db, owner_id, shop_data.shop_name)
        if existing:
            raise HTTPException(status_code=400, detail="Shop already exists for this owner")

        shop = Shop(
            owner_id=owner_id,
            shop_name=shop_data.shop_name,
            address=shop_data.address,
            city=shop_data.city,
            state=shop_data.state,
            open_time=shop_data.open_time,
            close_time=shop_data.close_time,
        )

        new_shop = await ShopRepository.create_shop(db, shop)
        return {"message": "Shop created successfully", "shop_id": new_shop.shop_id}

    @staticmethod
    async def book_slots(db, user_id: int, barber_id: int, shop_id: int, slot_ids: list[int]):
        booked_slots = []
        for slot_id in slot_ids:
            slot = await ShopRepository.get_slot_by_id(db, slot_id, shop_id)
            if not slot:
                raise HTTPException(status_code=404, detail=f"Slot {slot_id} not found")
            if slot.is_booked:
                raise HTTPException(status_code=400, detail=f"Slot {slot_id} already booked")

            slot.is_booked = True
            slot.status = "booked"

            booking = Booking(
                user_id=user_id,
                barber_id=barber_id,
                shop_id=shop_id,
                slot_id=slot.slot_id,
                booking_date=slot.slot_date,
                booking_time=slot.slot_time,
                status="booked",
            )
            await ShopRepository.create_booking(db, booking)

            booked_slots.append({
                "slot_id": slot.slot_id,
                "slot_date": str(slot.slot_date),
                "slot_time": str(slot.slot_time),
                "status": booking.status
            })

        return {
            "message": f"{len(booked_slots)} slots booked successfully",
            "user_id": user_id,
            "barber_id": barber_id,
            "shop_id": shop_id,
            "booked_slots": booked_slots
        }
