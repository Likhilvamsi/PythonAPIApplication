from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.db.database import get_db
from src.services.shop_service import ShopService
from src.schemas.shop_schemas import ShopCreate, ShopResponse, SlotResponse, BookingRequest
from src.core.logger import logger

router = APIRouter()

@router.get("/shops/", response_model=List[ShopResponse])
async def get_shops(db: AsyncSession = Depends(get_db)):
    logger.info("API call: GET /shops")
    return await ShopService.get_shops_for_user(db)

@router.get("/shops/{shop_id}/slots/", response_model=List[SlotResponse])
async def get_slots(shop_id: int, date: str = Query(..., description="Date in YYYY-MM-DD format"), db: AsyncSession = Depends(get_db)):
    logger.info(f"API call: GET /shops/{shop_id}/slots")
    return await ShopService.get_available_slots(db, shop_id, date)

@router.get("/owner/{owner_id}")
async def get_shops_by_owner(owner_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"API call: GET /shops/owner/{owner_id}")
    return await ShopService.get_shops_by_owner(db, owner_id)

@router.post("/book-slots/")
async def book_slots(request: BookingRequest, db: AsyncSession = Depends(get_db)):
    logger.info("API call: POST /shops/book-slots")
    return await ShopService.book_slots(db, request.user_id, request.barber_id, request.shop_id, request.slot_ids)

@router.post("/create")
async def create_shop(shop: ShopCreate, owner_id: int, db: AsyncSession = Depends(get_db)):
    logger.info("API call: POST /shops/create")
    return await ShopService.create_shop_if_not_exists(db, owner_id, shop)
