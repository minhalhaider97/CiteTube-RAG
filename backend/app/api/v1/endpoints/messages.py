from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.db.models.chat import Chat, Message
from app.schemas.chat import MessageCreateRequest, MessageResponse

router = APIRouter()

@router.post("/{chat_id}", response_model=MessageResponse, status_code=201)
def add_message(chat_id: int, payload: MessageCreateRequest, db: Session = Depends(get_db)):
    chat = db.scalar(select(Chat).where(Chat.id == chat_id, Chat.user_id == payload.user_id))
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")
    message = Message(chat_id=chat.id, role=payload.role, content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

@router.get("/{chat_id}", response_model=list[MessageResponse])
def list_messages(chat_id: int, user_id: str, db: Session = Depends(get_db)):
    chat = db.scalar(select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id))
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")
    return list(db.scalars(select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)))
