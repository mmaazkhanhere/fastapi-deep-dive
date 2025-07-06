# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Status": "FastAPI Server Running"}

@app.get("/items/{item_id}")  #sames as localhost:8000/items/1
def read_item(item_id: int):
    return {"Item ID is: ": item_id}