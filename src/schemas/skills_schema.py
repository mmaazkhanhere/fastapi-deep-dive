from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class SkillBase(BaseModel):
    title: str = Field(description="Title of the skill", min_length=1)
    description: str = Field(description="Description of the skill", min_length=1)

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: int = Field(description="Id of the skill", ge=1)
    created_at: datetime = Field(description="When it was created")

    model_config = ConfigDict(from_attributes=True)