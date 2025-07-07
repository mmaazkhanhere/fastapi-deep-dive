from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse, JSONResponse


app: FastAPI = FastAPI()

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

async def common_user_parameters(username: str, password: str, name: str | None = None):
    return {"username": username, "password": password, "name": name}


UserDep = Annotated[dict, Depends(common_user_parameters)]

@app.get("/items/")
async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons

@app.get("/users")
def get_users(user: UserDep):
    return user

