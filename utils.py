import base62
import random
import traceback
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from db import URL
import time

# Base62 encoding
def generate_short_url(id: int) -> str:
    random_seed = int(time.time() * 1000)
    modified_id = id + random_seed
    encoded = base62.encode(modified_id)
    return encoded.zfill(7)[:7]

# TTL management
def calculate_expiry(ttl: int) -> datetime:
    return datetime.UTC() + timedelta(days=ttl)

# Save to database
async def save_url(db: AsyncSession, long_url: str, ttl: int):
    db_url = URL(long_url=long_url, created_at=datetime.now(), ttl=ttl)
    db.add(db_url)
    try:
        # First commit to get the ID
        await db.commit()
        await db.refresh(db_url)
        
        # Generate short URL
        short_url = generate_short_url(db_url.id)
        db_url.short_url = short_url
        
        # Second commit for the short URL
        await db.commit()
        return db_url
    except Exception as e:
        print(traceback.format_exc())
        await db.rollback()