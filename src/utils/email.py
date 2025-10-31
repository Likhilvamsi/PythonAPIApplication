import smtplib
from fastapi import HTTPException
from src.core.logger import logger
from src.core.config import SMTP_EMAIL, SMTP_PASSWORD

async def send_email_otp(receiver_email: str, otp: str):
    subject = "Your OTP Verification Code"
    body = f"Your OTP is {otp}. It will expire in 5 minutes."
    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, receiver_email, message)
        logger.info(f"OTP sent successfully to {receiver_email}")
    except Exception as e:
        logger.error(f"Failed to send OTP to {receiver_email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP. Try again later.")
