from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = Field(default=None, pattern=r'^\d{10}$')
    role: Literal["customer", "owner"]

class OTPRequest(BaseModel):
    email: EmailStr
    role: Literal["customer", "owner"]

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str
    role: Literal["customer", "owner"]

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: str

class OTPLogin(BaseModel):
    email: EmailStr
    otp: str