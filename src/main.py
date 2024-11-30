from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routers import create, redirect, analytics
from db import init_db
from simple_queue import RedisClient
from config import settings
import logging
from logger_utils import setup_logging
setup_logging() ## added logging support, cause no one loves print statements in production

app = FastAPI()

@app.on_event("startup")
async def startup():
    ## Ensure we have db and redis server setup. Else the app functionality would break
    await init_db()
    await RedisClient.get_instance()
    # startup_queuing_server()
    logging.info("Starting server")

@app.on_event("shutdown")
async def shutdown():
    await RedisClient.close_instance()

# Diff routes for every feature. This makes it extensible
# We can keep adding features into its respective routers
app.include_router(create.router, prefix="/create")
app.include_router(analytics.router, prefix='/analytics')
app.include_router(redirect.router)

@app.get('/')
async def home_page():
    return RedirectResponse(url='/docs')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host='0.0.0.0',
        port=int(settings.app_port),
        reload=True if settings.debug else False
    )
