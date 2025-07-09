from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from src.schemas.skills_schema import Skill
from src.schemas.learning_resource_schema import LearningResource

class UserRole(Enum):
    learner = "learner"
    admin = "admin"
    contributor = "contributor"

class UserBase(BaseModel):
    name: str = Field(description="Full name of the user", min_length=1)
    email: EmailStr = Field(description="Email of the user")
    password: str = Field(description="password")
    is_active: bool = Field(description="Is the user active")
    role: UserRole = Field(description="Access role of the user")

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int = Field(description="Id of the user", ge=1)
    skills: list[Skill] = Field(description="Skills of the user", default=[])
    resources: list[LearningResource] = Field(description="Resources of the user", default=[])
    created_at: datetime = Field(description="Creation timestamp of the user", default=datetime.now())


class UserResponse(BaseModel):
    id: int = Field(description="Id of the user")
    name: str = Field(description="Name of the user")
    email: EmailStr = Field(description="Email of the user")
    is_active: bool = Field(description="Is the user active")
    role: UserRole = Field(description="Access role of the user")

    model_config = ConfigDict(from_attributes=True)

class UserCredentials(BaseModel):
    email: EmailStr = Field(description="Email of the user")
    password: str = Field(description="password")
