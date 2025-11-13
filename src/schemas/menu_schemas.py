from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MenuBase(BaseModel):
    service_name: str
    description: Optional[str]
    price: float
    duration_minutes: int
    is_active: Optional[bool] = True

class MenuCreate(MenuBase):
    shop_id: int
    owner_id: int

class MenuResponse(MenuBase):
    menu_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        
class MenuUpdate(BaseModel):
    owner_id: int
    service_name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    duration_minutes: Optional[int]