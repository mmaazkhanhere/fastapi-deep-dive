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
    

@skill_router.post("/create", status_code=status.HTTP_201_CREATED, description="Create a new skill")
async def create_skill(skill: SkillCreate, session: AsyncSession = Depends(get_async_session), current_user: dict = Depends(get_current_contributor_or_admin_user)):
    try:
        await SkillService(session).create_skill(skill)
        return {"message": "Skill Created", "status": 201}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating skill: {str(e)}")
    

@skill_router.get('/{skill_id}', status_code=status.HTTP_200_OK, description="Get skill of a given ID")
async def get_skill_by_id(skill_id: int, session: AsyncSession = Depends(get_async_session))->Skill:
    try:
        skill = await SkillService(session).get_skill_by_id(skill_id)
        if skill is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
        return skill
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting skill: {str(e)}")