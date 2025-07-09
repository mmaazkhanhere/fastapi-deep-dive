from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.security import get_current_contributor_or_admin_user
from src.backend.session import get_async_session
from src.schemas.skills_schema import Skill, SkillCreate
from src.services.skill_service import SkillService
from fastapi import HTTPException

skill_router: APIRouter =  APIRouter(prefix="/skills", tags=["Skill"])

@skill_router.get("/", status_code=status.HTTP_200_OK, description="Get all skills created")
async def get_skills(session: AsyncSession = Depends(get_async_session)) -> list[Skill]:
    try:
        skills = await SkillService(session).get_all_skills()
        return skills
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting skills: {str(e)}")