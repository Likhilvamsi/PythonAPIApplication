from sqlalchemy.future import select
from fastapi import HTTPException
from src.db.models import Menu, Shop
from src.core.logger import logger

class MenuRepository:

    @staticmethod
    async def get_menu_by_shop(db, shop_id: int):
        logger.info(f"Fetching menu for shop_id={shop_id}")
        result = await db.execute(select(Menu).filter(Menu.shop_id == shop_id))
        menu_items = result.scalars().all()
        return menu_items

    @staticmethod
    async def create_menu_item(db, menu_obj):
        logger.info(f"Creating menu item: {menu_obj.service_name}")
        db.add(menu_obj)
        await db.commit()
        await db.refresh(menu_obj)
        return menu_obj

    @staticmethod
    async def get_shop_by_owner(db, owner_id: int, shop_id: int):
        result = await db.execute(select(Shop).filter(Shop.owner_id == owner_id, Shop.shop_id == shop_id))
        return result.scalar_one_or_none()

    # New function — check if same menu already exists
    @staticmethod
    async def get_existing_menu_item(db, shop_id: int, service_name: str, price: float, duration_minutes: int):
        result = await db.execute(
            select(Menu).filter(
                Menu.shop_id == shop_id,
                Menu.service_name == service_name,
                Menu.price == price,
                Menu.duration_minutes == duration_minutes
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_menu_by_id(db, menu_id: int):
        result = await db.execute(select(Menu).filter(Menu.menu_id == menu_id))
        return result.scalar_one_or_none()

    #  New: Update menu item
    @staticmethod
    async def update_menu_item(db, menu: Menu):
        await db.commit()
        await db.refresh(menu)
        return menu