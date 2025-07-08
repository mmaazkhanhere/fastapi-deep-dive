from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# hash password entered by user
async def get_password_hash(password: str):
    return pwd_context.hash(password)

# verify password enter by user
async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
