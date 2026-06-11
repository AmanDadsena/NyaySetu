from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.db.database import get_db
from app.db.models import Message, User

router = APIRouter(prefix="/api/chat", tags=["chat"])

class MessageCreate(BaseModel):
    receiver_id: int
    content: str
    case_id: int | None = None

class MessageResponse(BaseModel):
    id: int
    content: str
    sender_id: int
    receiver_id: int
    case_id: int | None
    created_at: datetime

@router.post("/{sender_id}", response_model=MessageResponse)
async def send_message(sender_id: int, message: MessageCreate, db: AsyncSession = Depends(get_db)):
    new_message = Message(
        sender_id=sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
        case_id=message.case_id
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

@router.get("/{user1_id}/{user2_id}", response_model=List[MessageResponse])
async def get_messages(user1_id: int, user2_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import or_, and_
    result = await db.execute(
        select(Message).where(
            or_(
                and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
                and_(Message.sender_id == user2_id, Message.receiver_id == user1_id)
            )
        ).order_by(Message.created_at.asc())
    )
    return result.scalars().all()
