from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.learning_resource_schema import LearningResourceCreate
from src.backend.session import get_async_session
from src.services.resource_service import LearningResourceService

resource_router: APIRouter = APIRouter(prefix="/resources", tags=["Learning Resource"])

@resource_router.post("/create", status_code=status.HTTP_201_CREATED, description="Creates a learning resource")
async def create_resource(resource_data: LearningResourceCreate, session: AsyncSession = Depends(get_async_session)):
    try:
        await LearningResourceService(session).create_new_resource(resource_data)
        return {"message": "Learning Resource Created", "status": 201}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating resource: {str(e)}")