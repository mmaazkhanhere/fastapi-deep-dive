import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()

DB_DRIVER_NAME = os.getenv("DB_DRIVER_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")


if DB_DRIVER_NAME is None:
    raise ValueError("DB_DRIVER_NAME must not be None")

if DB_PORT is None:
    raise ValueError("DB_PORT must not be None")

DATABASE_URL = URL.create(
    drivername=DB_DRIVER_NAME,
    username=DB_USERNAME,
    password=DB_PASSWORD,
    host=DB_HOST,
    database=DB_NAME,
    port=int(DB_PORT)
)
