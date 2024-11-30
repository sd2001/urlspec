from fastapi import FastAPI
from routers import create, redirect, analytics
from db import init_db
from simple_queue import RedisClient, startup_queuing_server
from config import settings
import logging
from logger_utils import setup_logging
setup_logging()

# Initialize FastAPI app
app = FastAPI()

# Initialize database and Redis queue
@app.on_event("startup")
async def startup():
    await init_db()
    await RedisClient.get_instance()
    # startup_queuing_server()
    logging.info("Starting server")

@app.on_event("shutdown")
async def shutdown():
    await RedisClient.close_instance()

# Routers
app.include_router(create.router)
app.include_router(redirect.router)
app.include_router(analytics.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host='0.0.0.0',
        port=int(settings.app_port),
        reload=True if settings.debug else False
    )
