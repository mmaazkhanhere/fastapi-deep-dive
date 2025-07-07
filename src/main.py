from fastapi import FastAPI

app: FastAPI = FastAPI(title="Learning Path API", version="0.1.0")

@app.get('/status')
def get_fastapi_status():
    return {"Status": "FastAPI Service Running"}