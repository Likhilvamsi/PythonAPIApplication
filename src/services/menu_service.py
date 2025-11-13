from fastapi import HTTPException
from src.repositories.menu_repo import MenuRepository
from src.db.models import Menu

class MenuService:

    @staticmethod
    async def add_menu_item(
        db,
        owner_id: int,
        shop_id: int,
        service_name: str,
        description: str,
        price: float,
        duration_minutes: int  
    ):
        # Verify the owner really owns this shop
        shop = await MenuRepository.get_shop_by_owner(db, owner_id, shop_id)
        if not shop:
            raise HTTPException(status_code=403, detail="You are not authorized to add menu items to this shop")

        #  Check if service already exists (same service_name, price, duration)
        existing_menu = await MenuRepository.get_existing_menu_item(
            db, shop_id, service_name, price, duration_minutes
        )

        #If same service already exists, either return it or update description
        if existing_menu:
            # Option A: Just return existing data
            # return existing_menu

            # Option B (Recommended): Update description if changed
            existing_menu.description = description or existing_menu.description
            existing_menu.is_active = True
            await db.commit()
            await db.refresh(existing_menu)
            return existing_menu

        #  Otherwise, create new menu item
        new_menu = Menu(
            shop_id=shop_id,
            service_name=service_name,
            description=description,
            price=price,
            duration_minutes=duration_minutes
        )

        menu = await MenuRepository.create_menu_item(db, new_menu)
        return menu

    @staticmethod
    async def get_shop_menu(db, shop_id: int):
        menu_items = await MenuRepository.get_menu_by_shop(db, shop_id)
        return [
            {
                "menu_id": m.menu_id,
                "service_name": m.service_name,
                "description": m.description,
                "price": float(m.price),
                "duration_minutes": m.duration_minutes,
                "is_active": m.is_active,
                "created_at": m.created_at
            } for m in menu_items
        ]
    @staticmethod
    async def update_menu_item(db, owner_id: int, menu_id: int,
                               service_name: str = None,
                               description: str = None,
                               price: float = None,
                               duration_minutes: int = None):

        # Check if menu exists
        menu = await MenuRepository.get_menu_by_id(db, menu_id)
        if not menu:
            raise HTTPException(status_code=404, detail="Menu item not found")

        # Verify ownership
        shop = await MenuRepository.get_shop_by_owner(db, owner_id, menu.shop_id)
        if not shop:
            raise HTTPException(status_code=403, detail="You are not authorized to update this menu")

        # Update only provided fields
        if service_name:
            menu.service_name = service_name
        if description:
            menu.description = description
        if price is not None:
            menu.price = price
        if duration_minutes is not None:
            menu.duration_minutes = duration_minutes

        updated_menu = await MenuRepository.update_menu_item(db, menu)
        return updated_menu
    