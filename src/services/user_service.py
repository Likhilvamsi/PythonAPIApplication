import random
from datetime import datetime, timedelta, timezone
import pytz
from fastapi import HTTPException, status
from src.db.models import User
from src.repositories.user_repo import UserRepository
from src.core.security import hash_password, verify_password
from src.utils.email import send_email_otp
from src.core.logger import logger


class UserService:
    """Service layer for handling user operations like registration, login, and OTP verification."""

    @staticmethod
    async def register_user(db, username, email, password, phone_number, role):
        existing_user = await UserRepository.get_user_by_email(db, email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        if phone_number and await UserRepository.get_user_by_phone(db, phone_number):
            raise HTTPException(status_code=400, detail="Phone number already registered")

        hashed_pw = hash_password(password)

        # Use Kolkata timezone
        kolkata_tz = pytz.timezone("Asia/Kolkata")
        current_time = datetime.now(kolkata_tz)

        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_pw,
            phone_number=phone_number,
            role=role,
            created_at=current_time,
        )

        await UserRepository.create_user(db, new_user)
        logger.info(f"New user registered successfully: {email}")
        return {"message": "User registered successfully"}

    @staticmethod
    async def send_verification_otp(db, email):
        user = await UserRepository.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        otp = str(random.randint(100000, 999999))

        # Kolkata timezone
        kolkata_tz = pytz.timezone("Asia/Kolkata")
        expiry_time = datetime.now(kolkata_tz) + timedelta(minutes=10)

        await UserRepository.store_otp(db, email, otp, expiry_time)
        await send_email_otp(email, otp)

        logger.info(f"OTP sent successfully to {email}")
        return {"message": "Verification OTP sent to your email"}

    @staticmethod
    async def login_with_password(db, email, password, role):
        user = await UserRepository.get_user_by_email(db, email)
        if not user or user.role != role:
            logger.warning(f"Invalid credentials attempt for {email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Incorrect password attempt for {email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        logger.info(f"User logged in successfully with password: {email}")
        return {
            "message": "Login successful",
            "user_id": user.id,
            "role": user.role  # ✅ Added role info
        }

    @staticmethod
    async def login_with_otp(db, email, otp):
        user = await UserRepository.get_user_by_email(db, email)
        if not user:
            logger.warning(f"No user found for email: {email}")
            raise HTTPException(status_code=404, detail="User not found")

        otp_record = await UserRepository.get_otp_by_email(db, email)
        if not otp_record:
            logger.warning(f"No OTP found for {email}")
            raise HTTPException(status_code=404, detail="OTP not found")

        if otp_record.otp_code != otp:
            logger.warning(f"Invalid OTP entered for {email}")
            raise HTTPException(status_code=400, detail="Invalid OTP")

        kolkata_tz = pytz.timezone("Asia/Kolkata")
        current_time = datetime.now(kolkata_tz)

        expiry_time = otp_record.otp_expiry
        if expiry_time.tzinfo is None:
            expiry_time = expiry_time.replace(tzinfo=kolkata_tz)

        if expiry_time < current_time:
            logger.warning(f"Expired OTP for {email}")
            raise HTTPException(status_code=400, detail="OTP expired")

        user.is_verified = True
        await db.commit()

        logger.info(f"User logged in successfully via OTP: {email}")
        return {
            "message": "Login successful using OTP",
            "user_id": user.id,
            "role": user.role  # 
        }
