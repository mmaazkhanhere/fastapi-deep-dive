# main.py
from fastapi import FastAPI, Query
from enum import Enum
from typing import List, Dict, Union, Annotated
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


@app.get('/items')
def get_items(query: Annotated[str | None, Query(max_length=50)]=None): #Here you are enforcing that the query parameter length should be less than 50 characters and default value is None
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if query:
        results.update({"query": query})
    return results

@app.get("/user")
def get_users(user_id: Annotated[str, Query(max_length=16, min_length=8)]):
    return user_id

@app.get("/all_users")
def get_all_users(user_ids: Annotated[list[str], Query(title="User ID", description="List of users id to get")]=[]): #http://localhost:8000/all_user?user_ids=%22123%22&user_ids=%22111%22
    #you can now send a list of users in query parameter instead of one item 
    return user_ids

# @app.get("/all_users") #this will give error
# def get_userss(user_ids: Annotated[list[str], None]=[]): #you can now send a list of users in query parameter instead of one item
#     return user_ids


@app.get("/user_name")
def get_user_name(username: Annotated[str, Query(
    alias="user-name", #change name of the variable passed (instead of username, it will be user-name). user-name is not a legal python variable name but still want to give it so this is how you do it
    max_length=16,
    min_length=6,
    title="User Name",
    description="User name to get"
)]):
    return username


@app.get("/user_dob")
def get_user_dob(user_dob: Annotated[str, Query(
    alias="user-dob",
    max_length=10,
    min_length=10,
    title="User DOB",
    description="User DOB to get",
    deprecated=True # display a warning message on docs that this is deprecated and not in use
)]):
    return user_dob