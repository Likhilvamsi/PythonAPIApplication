from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from src.jobs.otp_cleanup import delete_expired_otps
from src.jobs.slot_generator import generate_barber_slots
from src.core.logger import logger

scheduler = BackgroundScheduler()

def start_scheduler(app: FastAPI):
    try:
        scheduler.add_job(
            delete_expired_otps,
            "interval",
            minutes=5,
            id="delete_otps",
            replace_existing=True
        )

        scheduler.add_job(
            generate_barber_slots,
            "interval",
            minutes=60,
            id="slot_agent",
            replace_existing=True
        )

        scheduler.start()
        logger.info(" Scheduler started: OTP cleanup + Slot generator running")
    except Exception as e:
        logger.error(f" Failed to start scheduler: {str(e)}")

def shutdown_scheduler():
    try:
        scheduler.shutdown()
        logger.info("Scheduler shutdown successfully.")
    except Exception as e:
        logger.error(f" Error while shutting down scheduler: {str(e)}")
