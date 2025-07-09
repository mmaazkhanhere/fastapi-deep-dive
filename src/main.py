from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.backend.session import engine
from src.db.database import Base

from .routers.resource_router import resource_router
from .routers.auth_router import auth_router
from .routers.skill_router import skill_router

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Application startup")
    print("Initializing database....")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialized")
        yield
    
        print("Application shutdown")

app: FastAPI = FastAPI(lifespan=lifespan, title="Learning Path API", version="0.1.0")

app.include_router(resource_router)
app.include_router(auth_router)
app.include_router(skill_router)

@app.get('/status')
def get_fastapi_status():
    return {"Status": "FastAPI Service Running"}