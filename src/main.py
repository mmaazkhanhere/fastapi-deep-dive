from fastapi import FastAPI

app: FastAPI = FastAPI()

@app.get('/status')
def get_fastapi_status():
    return {"Status": "FastAPI Service Running"}