from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from pydantic import BaseModel, constr
from typing import List, Optional
from datetime import datetime
import html

from app.db.database import get_db
from app.db.models import Message, User, Case
from app.middleware import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

class MessageCreate(BaseModel):
    receiver_id: int
    content: constr(min_length=1, max_length=2000)
    case_id: Optional[int] = None

class MessageResponse(BaseModel):
    id: int
    content: str
    sender_id: int
    receiver_id: int
    case_id: Optional[int]
    created_at: datetime

@router.post("", response_model=MessageResponse)
async def send_message(
    message: MessageCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if message.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")

    # Verify receiver exists
    result = await db.execute(select(User).where(User.id == message.receiver_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Receiver not found")

    # If associated with a case, verify the case exists and user is part of it
    if message.case_id:
        case_result = await db.execute(select(Case).where(Case.id == message.case_id))
        case = case_result.scalars().first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        if current_user.id not in [case.client_id, case.lawyer_id]:
            raise HTTPException(status_code=403, detail="Not authorized to message on this case")

    sanitized_content = html.escape(message.content.strip())

    new_message = Message(
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        content=sanitized_content,
        case_id=message.case_id
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

@router.get("/{other_user_id}", response_model=List[MessageResponse])
async def get_messages(
    other_user_id: int, 
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Message).where(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id)
            )
        ).order_by(Message.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()
