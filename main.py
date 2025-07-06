# main.py
from fastapi import FastAPI, Query, Path
from enum import Enum
from typing import List, Dict, Union, Annotated
from pydantic import BaseModel, Field

class Item(BaseModel):
    model_config = {"extra": "forbid"}
    
    id: int = Field(description="Unique identifier for the item")
    name: str = Field(description="Name of the item")
    description: str | None = Field(description="Description of the item", default=None)
    price: float = Field(description="Price of the item")
    tax: float | None = Field(description="Tax to be paid on the item", default=None)


app = FastAPI()

@app.get("/")
def read_root():
    return {"Status": "FastAPI Server Running"}

# @app.get("/items/{item_id}")
# def read_items(item_id: Annotated[int, Path(title="The ID of the item to get")], query: Annotated[str|None, Query(alias="item-query")] = None):
#     results = {"item_id": item_id}
#     if query:
#         results.update({"query": query})
    return results

# @app.get("/items/{item_id}")
# async def read_items(
#     item_id: Annotated[int, Path(title="The ID of the item to get", ge=1)], q: str
# ):
#     results = {"item_id": item_id}
#     if q:
#         results.update({"q": q})
#     return results

@app.get("/items/")
async def read_items(filter_query: Annotated[Item, Query()]): #FastAPi will extract data and give you as a request query on the docs 
    # so instead of passing on as body, you can pass on as query parameter
    # if you send another query variable that is not present in the Item Schema, it will give you 200 status
    return filter_query