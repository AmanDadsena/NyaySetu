from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False) # "client" or "lawyer"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Lawyer specific profile info
    specialties = Column(String(255), nullable=True) # comma separated
    experience_years = Column(Integer, nullable=True)
    bar_council_id = Column(String(50), nullable=True, unique=True) # optional verification
    
    # Constraints
    __table_args__ = (
        CheckConstraint(role.in_(['client', 'lawyer']), name='check_valid_role'),
    )

    cases_as_client = relationship("Case", back_populates="client", foreign_keys="Case.client_id", cascade="all, delete-orphan")
    cases_as_lawyer = relationship("Case", back_populates="lawyer", foreign_keys="Case.lawyer_id")
    
    messages_sent = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id", cascade="all, delete-orphan")
    messages_received = relationship("Message", back_populates="receiver", foreign_keys="Message.receiver_id", cascade="all, delete-orphan")


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="open", nullable=False) # open, assigned, in_progress, closed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    client_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lawyer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(status.in_(['open', 'assigned', 'in_progress', 'closed']), name='check_valid_status'),
    )

    client = relationship("User", back_populates="cases_as_client", foreign_keys=[client_id])
    lawyer = relationship("User", back_populates="cases_as_lawyer", foreign_keys=[lawyer_id])
    messages = relationship("Message", back_populates="case", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=True, index=True)
    
    sender = relationship("User", back_populates="messages_sent", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="messages_received", foreign_keys=[receiver_id])
    case = relationship("Case", back_populates="messages")
