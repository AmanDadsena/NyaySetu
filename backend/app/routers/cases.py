from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.db.models import Case

router = APIRouter(prefix="/api/cases", tags=["cases"])

class CaseCreate(BaseModel):
    title: str
    description: str
    client_id: int

class CaseResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    client_id: int
    created_at: datetime

@router.post("", response_model=CaseResponse)
async def create_case(case: CaseCreate, db: AsyncSession = Depends(get_db)):
    new_case = Case(title=case.title, description=case.description, client_id=case.client_id)
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)
    return new_case

@router.get("", response_model=List[CaseResponse])
async def get_cases(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Case).order_by(Case.created_at.desc()))
    return result.scalars().all()
