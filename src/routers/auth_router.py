from datetime import timedelta

from fastapi import APIRouter, Depends, status, HTTPException, Form, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user_schema import UserCreate, UserResponse
from src.schemas.token_schema import Token
from src.backend.session import get_async_session
from src.backend.config import config
from src.backend.security import create_access_token
from src.services.user_service import UserService
from src.tasks import send_email_notification

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

class OAuth2EmailPasswordRequestForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        email: str = Form(..., description="User email", alias="email"),
        password: str = Form(..., description="User password"),
    ):
        super().__init__(username=email, password=password)

        
@auth_router.get("/", status_code=status.HTTP_200_OK, description="Get all users", response_model=list[UserResponse])
async def get_users(session: AsyncSession = Depends(get_async_session)):
    """FastAPI endpoint to get all users"""
    try:
        users = await UserService(session).get_all_users()
        return users
    except Exception as e:
        raise ValueError(f"Error while getting users: {e}")


@auth_router.post("/register", status_code=status.HTTP_201_CREATED, description="Register new users")
async def register_user(user: UserCreate, background_tasks: BackgroundTasks, session:AsyncSession = Depends(get_async_session)):
    """FastAPI endpoint to register user"""
    try:
        user = await UserService(session).create_new_user(user)
        if user == "User already exists":
            return {"message": "User already exists", "status": 400}
        background_tasks.add_task(send_email_notification, user.email, "Welcome to our platform", "Thank you for registering")
        return {"message": "User Created", "status": 201}
    except Exception as e:
        raise ValueError(f"Error while creating user: {e}")
    
    

@auth_router.post("/token", status_code=status.HTTP_200_OK, description="Login user", response_model=Token)
async def access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),  # Use standard form
    session: AsyncSession = Depends(get_async_session)
):

    user = await UserService(session).authenticate_user(
        form_data.username,  # Use 'username' field instead of 'email'
        form_data.password
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=config.token_expiry)
    access_token = create_access_token(data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires)

    return Token(access_token=access_token, token_type="bearer")
