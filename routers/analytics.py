from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db import SessionLocal, URL
from utils import pause_redirect

router = APIRouter()


async def get_db():
    async with SessionLocal() as db:
        yield db


@router.get("/analytics/{short_url}")
async def get_analytics(short_url: str, db: AsyncSession = Depends(get_db)):
    db_url = await URL.fetch_row_via_short_url(short_url=short_url)
    if not db_url:
        return pause_redirect(mssg='URL not found in our records')
    return {"short_url": short_url, "long_url": db_url.long_url, "access_count": db_url.access_count}
