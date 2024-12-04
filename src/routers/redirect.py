from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils import pause_redirect, is_expired, raise_error_for_invalid_url
from db import *
from simple_queue import RedisClient, increment_count  # Redis client instance
from datetime import datetime
import asyncio
from config import settings

router = APIRouter()


# Redirect URL
@router.get("/{short_url}")
async def redirect_url(short_url: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    ## Func Requirment 2 as per the assignment doc: Redirection
    # Check Redis cache for the mapping, if exitss
    redis_client = await RedisClient.get_instance()
    ## quering if the url exists in redis. As this is quicker and wont cause much traffic in
    ## db-writer instance
    long_url = await redis_client.get(short_url) if redis_client else None

    # If not found in Redis, then we check the database and update Redis
    if not long_url:
        db_url = await URL.fetch_row_via_short_url(short_url=short_url)
        
        ## Check if row exists or if url expired. Display mssg appropriately
        if not db_url:
            return pause_redirect(mssg='URL not found in our records')
        
        ## Check for expiry (optional feature)
        if is_expired(db_url=db_url):
            _ = await URL.remove_row_via_short_url(short_url=short_url)
            return pause_redirect(mssg='URL requested has expired its TTL') 

        long_url = db_url.long_url
        remaining_ttl = db_url.ttl - (datetime.utcnow() - db_url.created_at).days
        ## Setting url in redis for easy key value quering. In memory is a lot faster
        await redis_client.set(short_url, long_url, ex=max(remaining_ttl, 1))
        # updating analytics using background task, to prevent main thread from getting slow
        background_tasks.add_task(increment_count, short_url)


    return RedirectResponse(long_url)

