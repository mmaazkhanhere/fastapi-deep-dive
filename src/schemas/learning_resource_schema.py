from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

from src.schemas.skills_schema import Skill

class LearningResourceType(Enum):
    article = "article"
    video = 'video'
    course = 'course'
    book = 'book'

class LearningResourceBase(BaseModel):
    title: str = Field(..., description="Title of the learning resource")
    description: str | None = Field(description="Description of the learning resource", default=None)
    url: str = Field(..., description="URL of the learning resource")
    resource_type: LearningResourceType = Field(..., description="Type of the learning resource")
    difficulty: int = Field(..., description="Difficulty level of the learning resource", ge=1, le=5)

class LearningResourceCreate(LearningResourceBase):
    pass

class LearningResource(LearningResourceBase):
    id: int = Field(description="Unique id of the learning resource")
    created_at: datetime = Field(description="Creation timestamp of the learning resource", default=datetime.now())
    skills: list[Skill] = Field(description="Skill user can learn from the learning resource", default=[])

    model_config = ConfigDict(from_attributes=True)