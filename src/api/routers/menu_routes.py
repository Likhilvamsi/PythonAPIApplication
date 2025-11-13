from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.db.database import get_db
from src.services.menu_service import MenuService
from src.schemas.menu_schemas import MenuCreate, MenuResponse, MenuUpdate

router = APIRouter(prefix="/menu", tags=["Menu"])

@router.post("/add", response_model=MenuResponse)
async def add_menu_item(menu_data: MenuCreate, db: AsyncSession = Depends(get_db)):
    return await MenuService.add_menu_item(
        db=db,
        owner_id=menu_data.owner_id,
        shop_id=menu_data.shop_id,
        service_name=menu_data.service_name,
        description=menu_data.description,
        price=menu_data.price,
        duration_minutes=menu_data.duration_minutes
    )
    


@router.get("/shop/{shop_id}", response_model=List[MenuResponse])
async def get_menu(shop_id: int, db: AsyncSession = Depends(get_db)):
    return await MenuService.get_shop_menu(db, shop_id)


@router.put("/update/{menu_id}", response_model=MenuResponse)
async def update_menu_item(menu_id: int, menu_data: MenuUpdate, db: AsyncSession = Depends(get_db)):
    return await MenuService.update_menu_item(
        db=db,
        owner_id=menu_data.owner_id,
        menu_id=menu_id,
        service_name=menu_data.service_name,
        description=menu_data.description,
        price=menu_data.price,
        duration_minutes=menu_data.duration_minutes
    )