from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from packages.db.connection import get_session
from packages.db.repositories.user_repo import UserRepository
from config import settings

router       = APIRouter()
pwd_context  = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

class Token(BaseModel):
    access_token: str
    token_type:   str
    user_id:      str
    name:         str

class UserCreate(BaseModel):
    email:    str
    name:     str
    password: str

def create_token(user_id: str, email: str) -> str:
    expire  = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "email": email, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(
    token:   str    = Depends(oauth2_scheme),
    session = Depends(get_session)
):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET,
                             algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    await repo.update_last_seen(user_id)
    return user

@router.post("/register")
async def register(data: UserCreate, session = Depends(get_session)):
    repo     = UserRepository(session)
    existing = await repo.get_by_email(data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(data.password)
    user   = await repo.create(data.email, data.name, hashed)
    return {"id": str(user.id), "email": user.email, "name": user.name}

@router.post("/token", response_model=Token)
async def login(
    form:    OAuth2PasswordRequestForm = Depends(),
    session = Depends(get_session)
):
    repo = UserRepository(session)
    user = await repo.get_by_email(form.username)
    if not user or not pwd_context.verify(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(str(user.id), user.email)
    return Token(access_token=token, token_type="bearer",
                 user_id=str(user.id), name=user.name)

@router.get("/me")
async def me(user = Depends(get_current_user)):
    return {"id": str(user.id), "email": user.email,
            "name": user.name, "role": user.role}
