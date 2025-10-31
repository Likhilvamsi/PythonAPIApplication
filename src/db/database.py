from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from src.core.config import DATABASE_URL
from src.core.logger import logger

Base = declarative_base()

# Async setup for FastAPI routes
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Sync setup for background jobs (APScheduler, scripts)
sync_engine = create_engine(DATABASE_URL.replace("+aiomysql", "+pymysql"), echo=False)
SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

async def get_db():
    async with async_session() as session:
        yield session
