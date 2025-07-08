from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
import jwt

from .config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



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