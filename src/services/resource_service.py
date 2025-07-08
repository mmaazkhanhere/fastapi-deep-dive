from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.models import LearningResource
from src.schemas.learning_resource_schema import LearningResourceCreate, LearningResource as ILearningResource
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