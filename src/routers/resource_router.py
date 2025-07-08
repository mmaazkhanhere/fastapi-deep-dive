from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.learning_resource_schema import LearningResourceCreate, LearningResource
from src.backend.session import get_async_session
from src.services.resource_service import LearningResourceService

resource_router: APIRouter = APIRouter(prefix="/resources", tags=["Learning Resource"])

@resource_router.post("/create", status_code=status.HTTP_201_CREATED, description="Creates a learning resource")
async def create_resource(resource_data: LearningResourceCreate, session: AsyncSession = Depends(get_async_session)):
    """FastAPI endpoint to create a learning resource"""
    try:
        await LearningResourceService(session).create_new_resource(resource_data)
        return {"message": "Learning Resource Created", "status": 201}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating resource: {str(e)}")
    

@resource_router.get("/", status_code=status.HTTP_200_OK, description="Get All Learning Resources")
async def get_resources(session: AsyncSession = Depends(get_async_session))-> list[LearningResource]:
    """FastAPI endpoint to get all resources"""
    try:
        resources = await LearningResourceService(session).get_all_resources()
        return resources
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting resources: {str(e)}")
    

@resource_router.get('/{resource_id}', status_code=status.HTTP_200_OK, description="Get learning resource of a given ID")
async def get_resource_by_id(resource_id: int, session: AsyncSession = Depends(get_async_session))->LearningResource:
    """FastAPI endpoint to get a resource by ID"""
    try:
        resource = await LearningResourceService(session).get_resource_by_resource_id(resource_id)
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        return resource
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting resource: {str(e)}")
    

@resource_router.delete('/{resource_id}/delete', status_code=status.HTTP_200_OK, description="Delete a learning resource record")
async def delete_resource(resource_id: int, session: AsyncSession = Depends(get_async_session)):
    """FastAPI endpoint to delete a resource by ID"""
    try:
        resource = await LearningResourceService(session).delete_resource(resource_id)
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        return {"message": "Learning Resource Deleted", "status": 200}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting resource: {str(e)}")