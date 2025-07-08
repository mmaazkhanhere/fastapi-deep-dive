from fastapi import APIRouter, Depends,status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user_schema import User, UserCreate, UserResponse
from src.backend.session import get_async_session
from src.services.user_service import UserService

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", status_code=status.HTTP_201_CREATED, description="Register new users")
async def register_user(user: UserCreate, session:AsyncSession = Depends(get_async_session)):
    """FastAPI endpoint to register user"""
    try:
        user = await UserService(session).create_new_user(user)
        if user == "User already exists":
            return {"message": "User already exists", "status": 400}
        return {"message": "User Created", "status": 201}
    except Exception as e:
        raise ValueError(f"Error while creating user: {e}")
    
