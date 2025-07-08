from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# hash password entered by user
async def get_password_hash(password: str):
    return pwd_context.hash(password)

# verify password enter by user
async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# create access token for the user
# async def create_access_token(data: dict, expires_delta: timedelta|None = None):
#     to_encode = data.copy()
#     expire: datetime = datetime.now() + expires_delta
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
#     return encoded_jwt
