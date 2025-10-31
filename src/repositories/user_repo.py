from datetime import datetime, timedelta, timezone
from sqlalchemy.future import select
from src.db.models import User, EmailVerification  # ensure EmailVerification model exists
from src.core.logger import logger


class UserRepository:

    @staticmethod
    async def get_user_by_email(db, email: str):
        logger.info(f"Fetching user by email: {email}")
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_phone(db, phone: str):
        logger.info(f"Fetching user by phone: {phone}")
        result = await db.execute(select(User).filter(User.phone_number == phone))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db, user: User):
        logger.info(f"Creating new user: {user.email}")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_user(db, user: User):
        logger.info(f"Updating user: {user.email}")
        await db.commit()
        await db.refresh(user)
        return user

    
    @staticmethod
    async def store_otp(db, email: str, otp: str, expiry_time):
        existing_record = await db.execute(select(EmailVerification).filter(EmailVerification.email == email))
        record = existing_record.scalar_one_or_none()

        if record:
            record.otp_code = otp
            record.otp_expiry = expiry_time
        else:
            record = EmailVerification(email=email, otp_code=otp, otp_expiry=expiry_time)

        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record
    
    @staticmethod
    async def get_otp_by_email(db, email: str):
        """Fetch OTP record from email_verification table."""
        logger.info(f"Fetching OTP record for email: {email}")
        result = await db.execute(select(EmailVerification).filter(EmailVerification.email == email))
        return result.scalar_one_or_none()
