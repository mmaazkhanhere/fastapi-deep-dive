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
    

    async def create_skill(self, skill: SkillCreate):
        new_skill = Skills(
            title = skill.title
        )
        self.session.add(new_skill)
        await self.session.commit()
        await self.session.refresh(new_skill)
        return 
    
    async def get_skill_by_id(self, skill_id: int):
        result = await self.session.execute(select(Skills).where(Skills.id == skill_id))
        skill = result.scalars().first()
        if skill is None:
            return None
        return Skill.model_validate(skill)