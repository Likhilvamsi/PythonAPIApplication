from datetime import datetime, timedelta
from src.db.database import SessionLocal
from src.db.models import EmailVerification
from src.core.logger import logger

def delete_expired_otps():
    """Delete expired OTPs older than 5 minutes."""
    db = SessionLocal()
    try:
        expiration_time = datetime.utcnow() - timedelta(minutes=5)
        deleted_count = db.query(EmailVerification).filter(EmailVerification.created_at < expiration_time).delete()
        db.commit()
        logger.info(f"[OTP CLEANUP] Deleted {deleted_count} expired OTP records")
    except Exception as e:
        db.rollback()
        logger.error(f"[OTP CLEANUP ERROR] {str(e)}")
    finally:
        db.close()
