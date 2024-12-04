import base62
import random
import requests
import hashlib
import traceback
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse, HTMLResponse
from db import URL
from config import settings
import time

redirect_url_base = f"{settings.running_host}:{settings.app_port}" if settings.debug else f"{settings.running_host}"
redirect_url = f"{redirect_url_base}/docs"

def generate_short_url(id: int) -> str:
    ## Func Requirment 3 as per the assignment doc: Unique URLS
    ## Using: hashlib + base62 encoding for optimal uniqueness -> 7 char aliases
    random_seed = int(time.time() * 1000)
    combined_id = f"{id}-{random_seed}-{settings.encoding_salt}"
    hash_object = hashlib.sha256(combined_id.encode())
    hash_digest = hash_object.digest()
    
    truncated_hash = int.from_bytes(hash_digest[:6], byteorder="big")
    final_encoded_alias = base62.encode(truncated_hash)
    return final_encoded_alias.zfill(7)[:7]

def calculate_expiry(ttl: int) -> datetime:
    return datetime.UTC() + timedelta(days=ttl)

def is_expired(db_url) -> bool:
    if not db_url.ttl or not db_url.created_at:
        return False
    current_time = datetime.now(timezone.utc)
    created_at = db_url.created_at.replace(tzinfo=timezone.utc) if db_url.created_at.tzinfo is None else db_url.created_at
    expiration_time = created_at + timedelta(days=db_url.ttl)
    return current_time > expiration_time

async def save_url(db: AsyncSession, long_url: str, ttl: int):
    ## Here we first insert the long url into the row.
    ## Then we fetch the id and insert the short url into it
    ## Encoding done is based on the id of the row.
    ## In a distributed DB environment it might be a problem, but for single DB
    ## clusters this would work just fine
    db_url = URL(long_url=long_url, created_at=datetime.now(), ttl=ttl)
    db.add(db_url)
    try:
        # First commit to get the ID
        await db.commit()
        await db.refresh(db_url)
        short_url = generate_short_url(db_url.id)
        db_url.short_url = short_url
        
        # Second commit for the short URL
        await db.commit()
        return db_url
    except Exception as e:
        ## Rollback the entire row in case of error to prevent unused rows
        print(traceback.format_exc())
        await db.rollback()
        
def pause_redirect(mssg):
    html_content = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="5;url={redirect_url}" />
        </head>
        <body>
            <h1>{mssg}</h1>
            <p>Click here to go to <a href="{redirect_url}">Homepage Docs</a></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

def raise_error_for_invalid_url(long_url: str):
    if not long_url.startswith('http://') and not long_url.startswith('https://'):
        long_url = f"http://{long_url}"
    try:
        response = requests.head(long_url, timeout=2, allow_redirects=True)
        if response.status_code >= 404:
            print(response.status_code)
            return True
        
        return False
    except ConnectionError as e:
        return True
    except requests.exceptions.RequestException:
        return True