from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models import User

router = APIRouter(prefix="/api/lawyers", tags=["lawyers"])

class LawyerResponse(BaseModel):
    id: int
    name: str
    specialties: str | None
    experience_years: int | None

@router.get("", response_model=list[LawyerResponse])
async def get_lawyers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.role == "lawyer"))
    lawyers = result.scalars().all()
    return lawyers
