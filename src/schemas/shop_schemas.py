from pydantic import BaseModel
from datetime import time
from typing import List

class ShopCreate(BaseModel):
    shop_name: str
    address: str
    city: str
    state: str
    open_time: time
    close_time: time

class ShopResponse(BaseModel):
    shop_id: int
    shop_name: str
    address: str
    city: str
    state: str
    open_time: str
    close_time: str
    is_open: bool

class SlotResponse(BaseModel):
    slot_id: int
    barber_id: int
    barber_name: str
    slot_time: str
    status: str

class BookingRequest(BaseModel):
    user_id: int
    barber_id: int
    shop_id: int
    slot_ids: List[int]
