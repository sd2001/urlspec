import base62
import random
import hashlib
import traceback
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse, HTMLResponse
from db import URL
from config import settings
import time

redirect_url = f"{settings.running_host}:{settings.app_port}/docs" if settings.debug else f"{settings.running_host}/docs"

def generate_short_url(id: int) -> str:
    random_seed = int(time.time() * 1000)
    combined_id = f"{id}-{random_seed}-{settings.encoding_salt}"
    hash_object = hashlib.sha256(combined_id.encode())
    hash_digest = hash_object.digest()
    
    truncated_hash = int.from_bytes(hash_digest[:6], byteorder="big")
    final_encoded_alias = base62.encode(truncated_hash)
    return final_encoded_alias.zfill(7)[:7]

def calculate_expiry(ttl: int) -> datetime:
    return datetime.UTC() + timedelta(days=ttl)

async def save_url(db: AsyncSession, long_url: str, ttl: int):
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