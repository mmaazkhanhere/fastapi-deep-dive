from typing import Annotated
from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user_schema import UserCreate, UserResponse, UserCredentials
from src.schemas.token_schema import Token
from src.backend.session import get_async_session
from src.backend.config import config
from src.backend.security import create_access_token
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
    

@auth_router.get("/", status_code=status.HTTP_200_OK, description="Get all users", response_model=list[UserResponse])
async def get_users(session: AsyncSession = Depends(get_async_session)):
    """FastAPI endpoint to get all users"""
    try:
        users = await UserService(session).get_all_users()
        return users
    except Exception as e:
        raise ValueError(f"Error while getting users: {e}")
    

@auth_router.post("/token", status_code=status.HTTP_200_OK, description="Login user", response_model=Token)
async def access_token(user_credentials: UserCredentials, session: AsyncSession = Depends(get_async_session)):
    """FastAPI endpoint to login user"""

    user = await UserService(session).authenticate_user(user_credentials.email, user_credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=config.token_expiry)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return Token(access_token=access_token, token_type="bearer")
