# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from src.backend.config import config


Base = declarative_base()
