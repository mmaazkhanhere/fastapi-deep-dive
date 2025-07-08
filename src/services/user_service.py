from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.models import User
from src.schemas.user_schema import UserCreate, UserResponse
from src.services.base import BaseService
from src.backend.security import get_password_hash, verify_password

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

    async def get_all_users(self):
        results = await self.session.execute(select(User))
        users = results.scalars().all()
        return [UserResponse.model_validate(user) for user in users]
    

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

        # 2. Verify password
        # Ensure that user.password is the hashed password from the DB
        if not await verify_password(password, user.hashed_password):
            print("Correct Password: False") # This print confirms a password mismatch
            return None # Password does not match

        print("Correct Password: True") # This would confirm a successful password match
        return user # Return the user object if authenticated