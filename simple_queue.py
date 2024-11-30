import aioredis
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import SessionLocal, URL
from config import settings
import logging
from logger_utils import setup_logging
setup_logging()

REDIS_URL = settings.redis_url
redis_client = None
    
class RedisClient:
    _instance = None

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = await aioredis.from_url(REDIS_URL, decode_responses=True)
        return cls._instance

    @classmethod
    async def close_instance(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None


async def increment_count(short_url):
    async with SessionLocal() as db:
        query = select(URL).where(URL.short_url == short_url)
        result = await db.execute(query)
        db_url = result.scalar_one_or_none()
        db_url.access_count += 1
        await db.commit()
        logging.info("Analytics IncremeUpdatednted")
    

# Background task to increment access counts in the database
# @router.on_event("startup")
# async def process_queue():
#     while True:
#         short_url = await dequeue_url()
#         if short_url:
#             async with SessionLocal() as db:
#                 query = select(URL).where(URL.short_url == short_url)
#                 result = await db.execute(query)
#                 db_url = result.scalar_one_or_none()
#                 if db_url:
#                     db_url.access_count += 1
#                     await db.commit()

# @router.on_event("startup")
async def startup_queuing_server():
    """
    Schedule the process_queue function as a background task.
    """
    asyncio.create_task(process_queue())
