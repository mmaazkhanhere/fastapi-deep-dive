# main.py
from fastapi import FastAPI
from enum import Enum
from typing import List, Dict, Union

app = FastAPI()

class ItemInventoryStatus(str, Enum):
    in_stock = "Available"
    out_of_stock = "Out of Stock"

items = [
    {
        "id": 1,
        "item": "Milk",
        "price": 15.6,
        "status": ItemInventoryStatus.in_stock
    },
    {
        "id": 2,
        "item": "Bread",
        "price": 10.5,
        "status": ItemInventoryStatus.out_of_stock
    },
    {
        "id": 3,
        "item": "Eggs",
        "price": 20.0,
        "status": ItemInventoryStatus.in_stock
    },
    {
        "id": 4,
        "item": "Cheese",
        "price": 30.0,
        "status": ItemInventoryStatus.out_of_stock
    },
    {
        "id": 5,
        "item": "Yogurt",
        "price": 25.0,
        "status": ItemInventoryStatus.in_stock
    },
    {
        "id": 6,
        "item": "Chicken",
        "price": 40.0,
        "status": ItemInventoryStatus.out_of_stock
    },
    {
        "id": 7,
        "item": "Beef",
        "price": 50.0,
        "status": ItemInventoryStatus.in_stock
    },
    {
        "id": 8,
        "item": "Pork",
        "price": 35.0,
        "status": ItemInventoryStatus.out_of_stock
    },
    {
        "id": 9,
        "item": "Fish",
        "price": 45.0,
        "status": ItemInventoryStatus.in_stock
    },
    {
        "id": 10,
        "item": "Shrimp",
        "price": 55.0,
        "status": ItemInventoryStatus.out_of_stock
    }
]

@app.get("/")
def read_root():
    return {"Status": "FastAPI Server Running"}

@app.get("/items/{item_id}")  #sames as localhost:8000/items/1
def read_item(item_id: int): #these are the parameters required to consume the api. They cannot have default values because are required fields
    return {f"Item with id {item_id}: ": items[item_id-1].get("item")}
    

@app.get("/items")
def get_item(id: Union[int, None] = None): #same as localhost:8000/items?id=1 They can have default values because they are not required fields
    if id is not None:
        return {f"Item with id {id}: ": items[id-1].get("item")}
    else:
        return {"All items: ": items}
    

@app.get("/items/{item_id}/status") #same as localhost:8000/1/status?status=Available
def get_item_statuses(item_id: int, status: Union[ItemInventoryStatus, None] = None ): # item_id is required field (path parameter) and status can have default value (query parameter)

    if status == ItemInventoryStatus.in_stock:
        return {"Item available"}
    else:
        return {"Out of stock"}


@app.get("/items/")
def get_item_price(item_id: int, price: bool=False): #Here the item_id is a required query parameter while price is optional query parameter. For a query parameter to be made optional, assign a default value
    if price:
        item_price = items[item_id-1].get("price")
        return {f"Item with id {item_id} price is: {item_price}"}
    else:
        return items[item_id-1]