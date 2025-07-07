from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession 

from src.schemas.learning_resource_schema import LearningResourceCreate
from src.backend.session import get_async_session # Import the async dependency
from src.services.resource_service import LearningResourceService

resource_router: APIRouter = APIRouter(prefix="/resources", tags=["Learning Resource"])

@resource_router.post('/', status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource: LearningResourceCreate,
    session: AsyncSession = Depends(get_async_session) 
):
    try:
        
        created_resource = await LearningResourceService(session).new_resource(resource)

        return created_resource
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal Server Error While Creating Resource: {e}")