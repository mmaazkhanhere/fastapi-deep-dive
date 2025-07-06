# main.py
from fastapi import FastAPI, Query, Path, Body
from enum import Enum
from typing import List, Dict, Union, Annotated
from pydantic import BaseModel, Field, EmailStr

class Item(BaseModel):
    model_config = {"extra": "forbid"}

    id: int = Field(description="Unique identifier for the item")
    name: str = Field(description="Name of the item")
    description: str | None = Field(description="Description of the item", default=None)
    price: float = Field(description="Price of the item", examples=["12.33"])
    tax: float | None = Field(description="Tax to be paid on the item", default=None)

class User(BaseModel):
    model_config = {"extra": "forbid"}

    id: int = Field(description="Unique identifier for the user")
    name: str = Field(description="Name of the user", max_length=50)
    email: EmailStr = Field(description="Email of the user")
    password: str = Field(description="Password of the user")


app = FastAPI()

@app.get("/")
def read_root():
    return {"Status": "FastAPI Server Running"}

# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_id": item_id, "item": item}

@app.put("/users/{user_id}")
def update_user(user_id: int, user: User, response_model=User):
    return {"user_id": user_id, "user": user}

@app.put('/update')
def update_all(item_id: int, item: Item, user: User):
    return {
        "item": item,
        "user": user
    }

@app.put('/user')
def update_user_data(user_id: int, user: User, session_id: Annotated[str, Body( 
    examples=[
        "adasdasdasd"
    ]
)]): # you are giving example of what the data will be like. It is already in the schema but here you are giving specific example
    return {
        "user_id": user_id,
        "user": user,
        "session_id": session_id
    }

@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Annotated[
        Item,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "different": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results