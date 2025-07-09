from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str = Field(description="Access token for user to use API")
    token_type: str = Field(description="Type of the token")

class TokenData(BaseModel):
    user_email: str | None = None