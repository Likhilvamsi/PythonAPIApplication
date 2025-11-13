import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pyinstrument import Profiler

from src.core.logger import logger
from src.core.scheduler import start_scheduler, shutdown_scheduler
from src.db.database import Base, engine
from src.api.routers import user_router, shop_routes, barber_routes, menu_routes


#  Middleware for profiling
class PyInstrumentMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        profiler = Profiler()
        profiler.start()

        response = await call_next(request)

        profiler.stop()
        # Print summary to console
        print(profiler.output_text(unicode=True, color=True))

        # Save detailed report for later inspection
        with open("pyinstrument_report.txt", "w", encoding="utf-8") as f:
            f.write(profiler.output_text(unicode=True))

        return response


# Initialize FastAPI application
app = FastAPI(
    title="Online Booking Application",
    description="Backend service for user, shop, and barber management with background schedulers.",
    version="1.0.0"
)

# Add the profiler middleware (only for development)
app.add_middleware(PyInstrumentMiddleware)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router.router, tags=["Users"])
app.include_router(shop_routes.router, tags=["Shops"])
app.include_router(barber_routes.router, tags=["Barbers"])
app.include_router(menu_routes.router, tags=["Menu"])
# Application startup event
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully.")

    start_scheduler(app)
    logger.info("Application startup complete. Scheduler initialized.")


# Application shutdown event
@app.on_event("shutdown")
async def on_shutdown():
    shutdown_scheduler()
    logger.info("Application shutdown completed successfully.")


# Root endpoint
@app.get("/", tags=["Health Check"])
async def root():
    logger.info("Health check endpoint accessed.")
    return {"message": "Online Booking Application is running successfully."}


# Entry point
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
