from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils import pause_redirect
from db import SessionLocal, URL, get_db
from simple_queue import RedisClient, increment_count  # Redis client instance
from datetime import datetime
import asyncio
from config import settings

router = APIRouter()


# Redirect URL
@router.get("/{short_url}")
async def redirect_url(short_url: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # Check Redis cache for the mapping, if exitss
    redis_client = await RedisClient.get_instance()
    long_url = await redis_client.get(short_url) if redis_client else None

    # If not found in Redis, then we check the database and update Redis
    if not long_url:
        db_url = await URL.fetch_row_via_short_url(short_url=short_url)
        if not db_url:
            return pause_redirect(mssg='URL not found in our records') 

        long_url = db_url.long_url
        remaining_ttl = db_url.ttl - (datetime.utcnow() - db_url.created_at).days
        await redis_client.set(short_url, long_url, ex=max(remaining_ttl, 1))
        background_tasks.add_task(increment_count, short_url)


    return RedirectResponse(long_url)

