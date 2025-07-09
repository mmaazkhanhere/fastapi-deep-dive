import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .config import config

from src.schemas.token_schema import TokenData
from src.backend.session import get_async_session
from src.services.user_service import UserService


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# create access token for the user
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    if config.secret_key is None:
        raise ValueError("Missing secret key")
    encoded_jwt = jwt.encode(to_encode, config.secret_key, algorithm=config.algorithm)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSession = Depends(get_async_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if config.secret_key is None:
            raise ValueError("Missing secret key")
        
        if config.algorithm is None:
            raise ValueError ("Missing hashing algorithm")

        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
        user_email = payload.get("sub")
        if user_email is None:
            raise credentials_exception
        token_data = TokenData(user_email=user_email)
    except InvalidTokenError:
        raise credentials_exception
    user = await UserService(session).get_user_with_email(token_data.user_email)
    if user is None:
        raise credentials_exception
    return user