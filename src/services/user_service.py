from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


from src.db.models import User, Skills
from src.schemas.user_schema import UserCreate, UserResponse
from src.schemas.skills_schema import SkillCreate
from src.services.base import BaseService
from src.utils.auth_utils import get_password_hash, verify_password

class UserService(BaseService):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_new_user(self, user: UserCreate):
        user_email = user.email

        existing_user = await self.session.execute(select(User).where(User.email == user_email))

        if existing_user.scalars().first() is not None:
            return "User already exists"
        
        hashed_password = await get_password_hash(user.password)
        
        user_data = User(
            name=user.name,
            email=user_email,
            hashed_password=hashed_password,
            is_active=user.is_active,
            role = user.role.value
        )

        self.session.add(user_data)
        await self.session.commit()
        await self.session.refresh(user_data)
        return user_data

    async def get_all_users(self):
        results = await self.session.execute(select(User))
        users = results.scalars().all()
        return [UserResponse.model_validate(user) for user in users]
    
    async def get_user_with_email(self, email: str):
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none() 
        return UserResponse.model_validate(user)
    

    async def authenticate_user(self, email: str, password: str):
        """
        Authenticates a user by email and password.
        """
        # 1. Fetch user by email
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None # User not found


        if not await verify_password(password, user.hashed_password):
            print("Correct Password: False")
            return None 

        print("Correct Password: True") 
        return user 
    
    # Updated create_user_skill method
    async def create_user_skill(self, user_id: int, skill_data: SkillCreate): 
        user = await self.session.execute(select(User).where(User.id == user_id))
        user = user.scalar_one_or_none()

        if user is None:
            return None

        # Create skill with user_id instead of appending to relationship
        new_skill = Skills(title=skill_data.title, user_id=user.id) 
        self.session.add(new_skill)
        await self.session.commit()

        return user

    async def get_user_skill(self, user_id: int):
        # Use selectinload to eagerly load the skills relationship
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.skills))
            .where(User.id == user_id)
        )
        user = result.scalars().first()
        if user is None:
            return None
        return user.skills