import os
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr, validator
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from app.db.database import get_db
from app.db.models import User

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "nyaysetu_secret_key_dev_only")
ALGORITHM = "HS256"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str # 'client' or 'lawyer'
    specialties: str | None = None
    experience_years: int | None = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[0-9]", v):
            raise ValueError('Password must contain at least one number')
        return v
        
    @validator('role')
    def validate_role(cls, v):
        if v not in ['client', 'lawyer']:
            raise ValueError('Role must be client or lawyer')
        return v
        
    @validator('name')
    def validate_name(cls, v):
        name = v.strip()
        if len(name) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return name

class UserLogin(BaseModel):
    email: EmailStr
    password: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=60*24) # 24 hours
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    normalized_email = user.email.lower().strip()
    result = await db.execute(select(User).where(User.email == normalized_email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pw = pwd_context.hash(user.password)
    new_user = User(
        name=user.name.strip(),
        email=normalized_email,
        hashed_password=hashed_pw,
        role=user.role,
        specialties=user.specialties.strip() if user.specialties else None,
        experience_years=user.experience_years
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {
        "message": "User registered successfully", 
        "user_id": new_user.id,
        "role": new_user.role
    }

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    normalized_email = user.email.lower().strip()
    result = await db.execute(select(User).where(User.email == normalized_email))
    db_user = result.scalars().first()
    
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
        
    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
        
    token = create_access_token({"sub": str(db_user.id), "role": db_user.role})
    return {
        "access_token": token, 
        "token_type": "bearer", 
        "user": {
            "id": db_user.id, 
            "name": db_user.name, 
            "role": db_user.role
        }
    }
