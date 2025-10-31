from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.schemas.user_schemas import UserCreate, OTPRequest, UserLogin, OTPLogin
from src.services.user_service import UserService

router = APIRouter(prefix="/users")

@router.post("/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserService.register_user(db, user.username, user.email, user.password, user.phone_number, user.role)

@router.post("/send-verification-otp")
async def send_otp(request: OTPRequest, db: AsyncSession = Depends(get_db)):
    return await UserService.send_verification_otp(db, request.email)

@router.post("/login")
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db)):
    return await UserService.login_with_password(db, user.email, user.password, user.role)

@router.post("/login-with-otp")
async def login_with_otp(request: OTPLogin, db: AsyncSession = Depends(get_db)):
    return await UserService.login_with_otp(db, request.email, request.otp)

