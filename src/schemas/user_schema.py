from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class UserBase(BaseModel):
    name: str = Field(description="Full name of the user", min_length=1)
    email: EmailStr = Field(description="Email of the user")
    password: str = Field(description="password")
    is_active: bool = Field(description="Is the user active")

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int = Field(description="Id of the user", ge=1)
    created_at: datetime = Field(description="Creation timestamp of the user", default=datetime.now())


class UserResponse(BaseModel):
    id: int = Field(description="Id of the user")
    name: str = Field(description="Name of the user")
    email: EmailStr = Field(description="Email of the user")
    is_active: bool = Field(description="Is the user active")

    model_config = ConfigDict(from_attributes=True)

class UserCredentials(BaseModel):
    email: EmailStr = Field(description="Email of the user")
    password: str = Field(description="password")
