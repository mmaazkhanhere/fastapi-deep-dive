from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

class FormData(BaseModel):
    username: str
    password: str

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

items = {"foo": "The Foo Wrestlers"}

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()




app: FastAPI = FastAPI()

@app.post(
    "/items/",
    response_model=Item,
    summary="Create an item",
    description="Create an item with all the information, name, description, price, tax and a set of unique tags",
)
async def create_item(item: Item):
    return item

@app.post("/login/", response_description="The created item",)
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {
        "username": username, 
        "password": password
        }

@app.post("/user")
def get_user(data: Annotated[FormData, Form()]):
    return data;


@app.post("/files/")
async def create_fil(file: Annotated[bytes, File()]): # 'Content-Type: multipart/form-data' \
    return {"file_size", len(file)}

@app.post("/uploadfile/")
async def create_upload_file(
    file: Annotated[UploadFile, File(description="A file read as UploadFile")],
):
    return {"filename": file.filename}

@app.post("/multiple_files")
async def upload_multiple_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}

@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.get("/items-header/{item_id}")
async def read_item_header(item_id: str, tags=["Items"]):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"item": items[item_id]}


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    """A function that raises custom error depending on the name entered""" #
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}