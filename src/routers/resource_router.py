from uuid import uuid4
import shutil 
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from fastapi_cache.key_builder import default_key_builder
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.learning_resource_schema import LearningResourceCreate, LearningResource as ILearningResource
from src.db.models import LearningResource
from src.schemas.user_schema import User
from src.schemas.skills_schema import SkillCreate
from src.backend.session import get_async_session
from src.backend.security import get_current_contributor_or_admin_user, get_current_admin_user
from src.services.resource_service import LearningResourceService
from src.tasks import log_resource_view

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

resource_router: APIRouter = APIRouter(prefix="/resources", tags=["Learning Resource"])

async def get_resource_by_id_key_builder(
    func,
    *args,
    **kwargs,
):
    resource_id = kwargs.get("resource_id")
    if resource_id is None:
        return default_key_builder(func, *args, **kwargs)

    return f"{func.__module__}:{func.__name__}:resource_id={resource_id}"


@resource_router.get("/", status_code=status.HTTP_200_OK, description="Get All Learning Resources")
@cache(expire=60)
async def get_resources(session: AsyncSession = Depends(get_async_session))-> list[ILearningResource]:
    """FastAPI endpoint to get all resources"""
    try:
        resources = await LearningResourceService(session).get_all_resources()
        return resources
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting resources: {str(e)}")
    

@resource_router.post("/create", status_code=status.HTTP_201_CREATED, description="Creates a learning resource")
async def create_resource(resource_data: LearningResourceCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_contributor_or_admin_user)):
    """FastAPI endpoint to create a learning resource"""
    try:
        await LearningResourceService(session).create_new_resource(resource_data)
        await FastAPICache.clear(namespace="fastapi-cache")
        return {"message": "Learning Resource Created", "status": 201}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating resource: {str(e)}")
        

@resource_router.get('/{resource_id}', status_code=status.HTTP_200_OK, description="Get learning resource of a given ID")
@cache(expire=60, key_builder = get_resource_by_id_key_builder)
async def get_resource_by_id(resource_id: int, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_contributor_or_admin_user) )->ILearningResource:
    """FastAPI endpoint to get a resource by ID"""
    try:
        resource = await LearningResourceService(session).get_resource_by_resource_id(resource_id)
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        return resource
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting resource: {str(e)}")


@resource_router.put('/{resource_id}/update', status_code=status.HTTP_200_OK, description="Update a learning resource")
async def update_resource(resource_id: int, new_resource_data: LearningResourceCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_contributor_or_admin_user)):
    """FastAPI endpoint to update a resource"""
    try:
        resource = await LearningResourceService(session).update_resource(resource_id, new_resource_data)
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        await FastAPICache.clear(namespace="fastapi-cache")
        return resource
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating resource: {str(e)}")    


@resource_router.delete('/{resource_id}/delete', status_code=status.HTTP_200_OK, description="Delete a learning resource record")
async def delete_resource(resource_id: int, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_contributor_or_admin_user)):
    """FastAPI endpoint to delete a resource by ID"""
    try:
        resource = await LearningResourceService(session).delete_resource(resource_id)
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        await FastAPICache.clear(namespace="fastapi-cache")
        return {"message": "Learning Resource Deleted", "status": 200}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting resource: {str(e)}")
    

@resource_router.delete('/{resource_id}/admin/delete', status_code=status.HTTP_200_OK, description="Delete a learning resource record")
async def delete_admin_resource(resource_id: int, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_admin_user)):
    """FastAPI endpoint to delete a resource by ID"""
    try:
        resource = await LearningResourceService(session).delete_resource(resource_id)
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
        await FastAPICache.clear(namespace="fastapi-cache")
        return {"message": "Learning Resource Deleted", "status": 200}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting resource: {str(e)}")
    

@resource_router.post("/resources/{resource_id}/skills/{skill_id}", status_code=status.HTTP_200_OK, description="Create skill for a given resource")
async def add_skill_to_resource(
    resource_id: int,
    user_id: int,
    skill_data: SkillCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_contributor_or_admin_user)
):
    service = LearningResourceService(session)
    
    # Use SQLAlchemy model here
    skill = await service.learning_resource_skill(resource_id, user_id, skill_data) 
        
    if skill is None:
        # This means the resource was not found by the service method
        raise HTTPException(status_code=404, detail="Resource not found or skill could not be associated.")

    await FastAPICache.clear(namespace="fastapi-cache")
    # Return the associated skill or a confirmation message
    return {"message": "Skill added to resource successfully", "skill": skill}


@resource_router.delete("/resources/{resource_id}/skills/{skill_id}/delete", status_code=status.HTTP_200_OK, description="Delete skill for a given resource")
async def delete_skill_from_resource(
    resource_id: int,
    user_id: int,
    skill_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_contributor_or_admin_user)
):
    service = LearningResourceService(session)
    resource = await session.get(LearningResource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    skill = await service.delete_learning_resource_skill(resource_id, user_id, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@resource_router.post("/{resource_id}/log_view", status_code=status.HTTP_200_OK)
def view_logs(resource_id: int, user_id:int, background_task: BackgroundTasks):
    background_task.add_task(log_resource_view, resource_id, user_id)
    return {"message": "View logged"}


@resource_router.post("/{resource_id}/upload_image", status_code=status.HTTP_200_OK, description="Upload image for the resource")
async def upload_resource_image(resource_id: int, image_file: UploadFile = File(...), session: AsyncSession = Depends(get_async_session)):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    STATIC_DIR = BASE_DIR / "static"
    RESOURCE_IMAGES_DIR = STATIC_DIR / "resource_images"


    file_extension = Path(image_file.filename).suffix
    unique_filename = f"{uuid4()}{file_extension}"

    full_file_path = RESOURCE_IMAGES_DIR / unique_filename

    print(f"Saving to: {full_file_path}")
    try:
        RESOURCE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

        if not image_file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed."
        )

        with open(full_file_path, "wb") as file_object: 
            shutil.copyfileobj(image_file.file, file_object)
            
            image_url = f"/static/resource_images/{unique_filename}"

            await LearningResourceService(session).add_image_resource(resource_id, image_url)
            
            return {
                "message": "Image uploaded successfully",
                "filename": unique_filename,
                "content_type": image_file.content_type,
                "file_size": image_file.size,
                "image_url": image_url
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}"
        )
    finally:
        image_file.file.close()