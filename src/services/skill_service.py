from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.services.base import BaseService
from src.db.models import Skills
from src.schemas.skills_schema import SkillCreate, Skill


class SkillService(BaseService):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_skills(self):
        result = await self.session.execute(select(Skills))
        skills = result.scalars().all()
        return [Skill.model_validate(skill) for skill in skills]