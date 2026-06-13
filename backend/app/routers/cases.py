from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, constr
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.db.models import Case, User
from app.middleware import get_current_user

router = APIRouter(prefix="/api/cases", tags=["cases"])

class CaseCreate(BaseModel):
    title: constr(min_length=5, max_length=200)
    description: constr(min_length=10, max_length=5000)

class CaseResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    client_id: int
    lawyer_id: Optional[int]
    created_at: datetime
    updated_at: datetime

class CaseStatusUpdate(BaseModel):
    status: str

@router.post("", response_model=CaseResponse)
async def create_case(
    case: CaseCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can post cases")
        
    new_case = Case(
        title=case.title.strip(), 
        description=case.description.strip(), 
        client_id=current_user.id
    )
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)
    return new_case

@router.get("", response_model=List[CaseResponse])
async def get_cases(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "lawyer":
        # Lawyers see all open cases or their assigned cases
        result = await db.execute(select(Case).where(
            (Case.status == "open") | (Case.lawyer_id == current_user.id)
        ).order_by(Case.created_at.desc()))
    else:
        # Clients see only their own cases
        result = await db.execute(select(Case).where(
            Case.client_id == current_user.id
        ).order_by(Case.created_at.desc()))
        
    return result.scalars().all()

@router.patch("/{case_id}/assign", response_model=CaseResponse)
async def assign_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "lawyer":
        raise HTTPException(status_code=403, detail="Only lawyers can assign themselves to cases")
        
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalars().first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if case.status != "open" or case.lawyer_id is not None:
        raise HTTPException(status_code=400, detail="Case is already assigned or closed")
        
    case.lawyer_id = current_user.id
    case.status = "assigned"
    
    await db.commit()
    await db.refresh(case)
    return case

@router.patch("/{case_id}/status", response_model=CaseResponse)
async def update_case_status(
    case_id: int,
    status_update: CaseStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if status_update.status not in ["open", "assigned", "in_progress", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalars().first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Only the assigned lawyer or the case client can update the status
    if current_user.id not in [case.client_id, case.lawyer_id]:
        raise HTTPException(status_code=403, detail="Not authorized to update this case")
        
    case.status = status_update.status
    await db.commit()
    await db.refresh(case)
    return case
