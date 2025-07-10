from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.db.models import LearningResource, Skills
from src.schemas.learning_resource_schema import LearningResourceCreate, LearningResource as ILearningResource
from src.schemas.skills_schema import SkillCreate
from src.services.base import BaseService


class LearningResourceService(BaseService):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_new_resource(self, resource: LearningResourceCreate)-> LearningResource:
        db_resource = LearningResource(
            title=resource.title,
            description=resource.description,
            url=resource.url,
            resource_type=resource.resource_type.value,
            difficulty=resource.difficulty
        )
        self.session.add(db_resource)
        await self.session.commit()
        await self.session.refresh(db_resource)
        return db_resource

    
    async def get_all_resources(self):
        result = await self.session.execute(select(LearningResource))
        resources = result.scalars().all()
        # Convert SQLAlchemy models to Pydantic schemas
        return [ILearningResource.model_validate(resource) for resource in resources]
    

    async def get_resource_by_resource_id(self, resource_id: int):
        result = await self.session.execute(select(LearningResource).where(LearningResource.id == resource_id))
        resource = result.scalars().first()
        if resource is None:
            return None
        return ILearningResource.model_validate(resource)
    

    async def delete_resource(self, resource_id: int):
        result = await self.session.execute(select(LearningResource).where(LearningResource.id == resource_id))
        resource = result.scalars().first()
        if resource is None:
            return None
        await self.session.delete(resource)
        await self.session.commit()
        return resource
    
    async def update_resource(self, resource_id: int, new_data: LearningResourceCreate):
        result = await self.session.execute(select(LearningResource).where(LearningResource.id == resource_id))
        resource = result.scalars().first()
        
        if resource is None:
            return None
        
        resource.title = new_data.title
        resource.description = new_data.description
        resource.url = new_data.url
        resource.resource_type = new_data.resource_type.value 
        resource.difficulty = new_data.difficulty


        await self.session.commit()
        await self.session.refresh(resource)
        
        return ILearningResource.model_validate(resource)


    async def learning_resource_skill(self, resource_id: int, user_id: int, skill_data: SkillCreate):
        result = await self.session.execute(
            select(LearningResource)
            .options(selectinload(LearningResource.skills))
            .where(LearningResource.id == resource_id)
        )
        resource = result.scalars().first()

        if resource is None:
            return None

        # Check for existing skill
        skill_result = await self.session.execute(
            select(Skills).where(
                Skills.title == skill_data.title,
                Skills.user_id == user_id
            )
        )
        existing_skill = skill_result.scalars().first()

        # Create new skill if needed
        if existing_skill:
            skill = existing_skill
        else:
            skill = Skills(title=skill_data.title, user_id=user_id)
            self.session.add(skill)
            await self.session.flush()

        # Associate skill with resource
        resource.skill_id = skill.id
        await self.session.commit()
        return skill  # Return only the skill object