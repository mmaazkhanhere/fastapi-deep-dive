import os
from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseModel):
    """
    Configuration parameters for the the PostgreSQL database backend
    
    This model defines the necessary connection details for SQLAlchemy to establish a connection to the database

    Attributes:
    dsn: Data source for connecting to the target database
    """
    dsn: str = "postgresql+asyncpg://postgres:password@localhost:5434/fastapi_db"
    
class Config(BaseSettings):
    """
    Main application configuration parameters for the FastAPI backend

    This class leverages Pydantic Bases Settings to automatically load the configuration values from various
    resources, prioritizing in the following order

    1- Environment variables
    2- .env variables
    3- Default values specified directly within the Config class

    Attributes:
    database: An embedded Pydantic model holding all database-specific configuration settings
    token_key: A secret key for security-related operations
    """
    database: DatabaseConfig = DatabaseConfig()
    token_key: str = ""

config = Config()
