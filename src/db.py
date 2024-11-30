from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from config import settings

 # Using sqlite for now. To change to mysql or postgres we just need to modify
 # the url, as the remaining functions via ORM would work same
DATABASE_URL = f"sqlite+aiosqlite:///./{settings.db_name}"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        

async def get_db():
    async with SessionLocal() as db:
        yield db

# URL model
class URL(Base):
    __tablename__ = settings.url_tablename
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String, nullable=False)
    short_url = Column(String, unique=True, index=True)
    created_at = Column(DateTime)
    ttl = Column(Integer)
    access_count = Column(Integer, default=0)
    
    @classmethod
    async def fetch_row_via_short_url(cls, *, short_url):
        async for db in get_db():
            query = select(URL).where(URL.short_url == short_url)
            result = await db.execute(query)
            db_url = result.scalar_one_or_none()
            return db_url
    
    @classmethod
    async def fetch_row_via_long_url(cls, *, long_url):
        async for db in get_db():
            query = select(URL).where(URL.long_url == long_url)
            result = await db.execute(query)
            db_url = result.scalar_one_or_none()
            return db_url
        
    @classmethod
    async def remove_row_via_short_url(cls, *, short_url):
        async for db in get_db():
            query = select(URL).where(URL.short_url == short_url)
            result = await db.execute(query)
            db_url = result.scalar_one_or_none()
            
            if db_url:
                await db.delete(db_url)
                await db.commit()
                return True
            return False
