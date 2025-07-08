from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.models import User
from src.schemas.user_schema import UserCreate
from src.services.base import BaseService
from src.backend.security import get_password_hash

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
        )

        self.session.add(user_data)
        await self.session.commit()
        await self.session.refresh(user_data)
        return user_data
