from sqlalchemy.ext.asyncio import AsyncSession 
from src.db.models import LearningResource
from src.services.base_service import BaseService 
from src.schemas.learning_resource_schema import LearningResourceCreate

class LearningResourceService(BaseService): 
    def __init__(self, session: AsyncSession): 
        self.session = session

    async def new_resource(self, resource: LearningResourceCreate) -> LearningResource: 
        
        db_resource = LearningResource(
            title=resource.title,
            description=resource.description,
            url=resource.url, 
            resource_type=resource.resource_type.value, 
            difficulty=resource.difficulty,
        )

        self.session.add(db_resource)
        await self.session.commit() 
        await self.session.refresh(db_resource) 
        return db_resource