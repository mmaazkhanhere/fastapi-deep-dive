import os
from dotenv import load_dotenv

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class DatabaseConfig(BaseModel):
    """
    Configuration for the Postgres database backend
    
    Attributes:
    dsn: Data source for connecting with the target database
    """

    db_url: str | None = os.getenv("DB_URL")
    if db_url is None:
        raise ValueError("Database url is missing")
    
    dsn: str = db_url


class Config(DatabaseConfig):
    """
    Main application configuration parameters for the FastAPI backend

    Attributes:
    database: An embedded Pydantic model holding all database specific configuration
    token: A secret key for security-related operations
    """

    database: DatabaseConfig = DatabaseConfig()
    secret_key: str | None = os.getenv("SECRET_KEY")
    token_expiry: int = 15
    algorithm: str | None = os.getenv("ALGORITHM")
    token_key: str = ""


config = Config()
