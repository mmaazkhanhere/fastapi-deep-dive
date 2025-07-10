from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.session import get_async_session
from src.backend.security import get_current_contributor_or_admin_user
from src.schemas.skills_schema import SkillCreate
from src.services.user_service import UserService

user_router = APIRouter(prefix="/user", tags=["User"])

@user_router.post('/me/skills', description="API endpoint to create skills for user", status_code=status.HTTP_201_CREATED)
async def user_skills(
    user_id: int,
    skill: SkillCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user = Depends(get_current_contributor_or_admin_user)
):
    try:
        user_skill = await UserService(session).create_user_skill(user_id, skill)
        if user_skill is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"message": "Skill Assigned to User", "status": 201}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while creating skill for user: {e}")


@user_router.get("/me/skills", description="API endpoint to get skills for user", status_code=status.HTTP_200_OK)
async def get_user_skills(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user = Depends(get_current_contributor_or_admin_user)
):
    try:
        user_skill = await UserService(session).get_user_skill(user_id)
        if user_skill is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user_skill
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error while getting skill for user: {e}")