# main.py
from fastapi import FastAPI
from enum import Enum
from typing import List, Dict, Union
from pydantic import BaseModel, Field

class Item(BaseModel):
    id: int = Field(description="Unique identifier for the item")
    name: str = Field(description="Name of the item")
    description: str | None = Field(description="Description of the item", default=None)
    price: float = Field(description="Price of the item")
    tax: float | None = Field(description="Tax to be paid on the item", default=None)


app = FastAPI()

@app.get("/")
def read_root():
    return {"Status": "FastAPI Server Running"}

# @app.post('/create_item')
# def create_item(item: Item): # we say that we will receive request body of schema Item and we are returning it
#     return item

@app.post('/create_item') # http://localhost:8000/create_item
def create_item(item: Item):
    if item.tax is not None:
        item.price = item.price + item.tax
        return item
    else:
        return item
    

@app.put("/items/{item_id}") # http://localhost:8000/items/1 (In practice, this is done to update an item of id {item_id} in the database with the new item details {item}.)
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}


