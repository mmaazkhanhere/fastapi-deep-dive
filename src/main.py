from fastapi import FastAPI

from .routers.resource_router import resource_router

app: FastAPI = FastAPI(title="Learning Path API", version="0.1.0")
app.include_router(resource_router)

@app.get('/status')
def get_fastapi_status():
    return {"Status": "FastAPI Service Running"}