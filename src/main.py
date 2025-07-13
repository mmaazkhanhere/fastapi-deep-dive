from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis

from src.backend.session import engine
from src.db.database import Base
from src.backend.config import config

from .routers.resource_router import resource_router
from .routers.auth_router import auth_router
from .routers.skill_router import skill_router
from .routers.user_router import user_router

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Application startup")
    print("Initializing database....")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialized")

        redis_client = aioredis.from_url(config.REDIS_URL, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
        print("FastAPI-Cache initialized with Redis.")

        yield
    
        print("Application shutdown")

app: FastAPI = FastAPI(lifespan=lifespan, title="Learning Path API", version="0.1.1")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(resource_router)
app.include_router(auth_router)
app.include_router(skill_router)
app.include_router(user_router)

@app.get('/status')
def get_fastapi_status():
    return {"Status": "FastAPI Service Running"}