from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List

from app.db.database import get_db
from app.db.models import User

router = APIRouter(prefix="/api/lawyers", tags=["lawyers"])

class LawyerResponse(BaseModel):
    id: int
    name: str
    specialties: str | None
    experience_years: int | None

@router.get("", response_model=List[LawyerResponse])
async def get_lawyers(
    limit: int = Query(50, le=100),
    offset: int = 0,
    specialty: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.role == "lawyer", User.is_active == True)
    
    if specialty:
        # Simple case-insensitive match for sqlite
        query = query.where(User.specialties.ilike(f"%{specialty}%"))
        
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    return result.scalars().all()
