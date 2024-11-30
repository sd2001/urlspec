from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from db import SessionLocal, URL
from utils import save_url, redirect_url_base
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


@router.post("/")
async def create_url(request: URLCreate, db: AsyncSession = Depends(get_db)):
    ## Func Requirment 4 as per the assignment doc: Validations
    if not validators.url(request.long_url):
        raise HTTPException(status_code=400, detail="URL not valid")
    ## Since this is made for a single user, for existing long urls, we would
    ## return the same short url alias instead of creating new rows
    existing_url = await URL.fetch_row_via_long_url(long_url=request.long_url)
    if existing_url:
        return URLResponse(
            short_alias=existing_url.short_url,
            shortened_url=redirect_url_base + "/" + existing_url.short_url
        )
    ## Func Requirment 1 as per the assignment doc: Shorten urls
    saved_url = await save_url(db, request.long_url, request.ttl)
    return URLResponse(
            short_alias=saved_url.short_url,
            shortened_url=f"{redirect_url_base}/{saved_url.short_url}"
        )
