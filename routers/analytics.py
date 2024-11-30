from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import SessionLocal, URL

router = APIRouter()

# Database dependency
async def get_db():
    async with SessionLocal() as db:
        yield db

# Analytics endpoint
@router.get("/analytics/{short_url}")
async def get_analytics(short_url: str, db: AsyncSession = Depends(get_db)):
    db_url = await URL.fetch_row_via_short_url(short_url=short_url)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"short_url": short_url, "long_url": db_url.long_url, "access_count": db_url.access_count}
