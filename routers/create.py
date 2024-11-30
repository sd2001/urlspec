from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from db import SessionLocal, URL
from utils import save_url
from config import settings
import validators

router = APIRouter()

async def get_db():
    async with SessionLocal() as db:
        yield db

class URLCreate(BaseModel):
    long_url: str
    ttl: int = 7
    
class URLResponse(BaseModel):
    short_alias: str
    shortened_url: str


@router.post("/create")
async def create_url(request: URLCreate, db: AsyncSession = Depends(get_db)):
    if not validators.url(request.long_url):
        raise HTTPException(status_code=400, detail="URL not valid")
    redirect_url = f"{settings.running_host}:{settings.app_port}/" if settings.app_port else f"{settings.running_host}/"
    existing_url = await URL.fetch_row_via_long_url(long_url=request.long_url)
    if existing_url:
        return URLResponse(
            short_alias=existing_url.short_url,
            shortened_url=redirect_url + existing_url.short_url
        )
    saved_url = await save_url(db, request.long_url, request.ttl)
    return URLResponse(
            short_alias=saved_url.short_url,
            shortened_url=redirect_url + saved_url.short_url
        )
