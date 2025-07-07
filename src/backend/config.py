import os
from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseModel):
    """Backend database configuration parameters.

    Attributes:
        dsn: DSN for target database.
    """
    dsn: str = "postgresql+asyncpg://postgres:password@localhost:5434/fastapi_db"
    
class Config(BaseSettings):
    """API configuration parameters.

    Automatically read modifications to the configuration parameters
    from environment variables and ``.env`` file.
    """
    database: DatabaseConfig = DatabaseConfig()
    token_key: str = ""

config = Config()
