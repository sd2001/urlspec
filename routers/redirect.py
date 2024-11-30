from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import SessionLocal, URL, get_db
from simple_queue import RedisClient, increment_count  # Redis client instance
from datetime import datetime
import asyncio
from config import settings

router = APIRouter()

def pause_redirect():
    redirect_url = f"{settings.running_host}:{settings.app_port}/docs" if settings.app_port else f"{settings.running_host}/docs"
    html_content = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="5;url={redirect_url}" />
        </head>
        <body>
            <h1>Redirecting you to another website...</h1>
            <p>You will be redirected to <a href="{redirect_url}">Homepage Docs</a> in 5 seconds.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Redirect URL
@router.get("/{short_url}")
async def redirect_url(short_url: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # Check Redis cache for the mapping
    redis_client = await RedisClient.get_instance()
    long_url = await redis_client.get(short_url) if redis_client else None

    # If not found in Redis, check the database and update Redis
    if not long_url:
        db_url = await URL.fetch_row_via_short_url(short_url=short_url)
        if not db_url:
            return pause_redirect() 

        # Save mapping in Redis with TTL equal to the remaining time
        long_url = db_url.long_url
        remaining_ttl = db_url.ttl - (datetime.utcnow() - db_url.created_at).days
        await redis_client.set(short_url, long_url, ex=max(remaining_ttl, 1))
        background_tasks.add_task(increment_count, short_url)


    return RedirectResponse(long_url)

