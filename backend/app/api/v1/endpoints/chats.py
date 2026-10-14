from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.db.models.chat import Chat
from app.db.models.video import Video
from app.schemas.chat import ChatCreateRequest, ChatResponse

router = APIRouter()

@router.post("", response_model=ChatResponse, status_code=201)
def create_chat(payload: ChatCreateRequest, db: Session = Depends(get_db)):
    video = db.get(Video, payload.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found.")
    if video.ingestion_status != "completed":
        raise HTTPException(status_code=409, detail="Video ingestion is not completed yet.")
    chat = Chat(user_id=payload.user_id, video_id=video.id, title=video.title)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

@router.get("", response_model=list[ChatResponse])
def list_chats(user_id: str = Query(min_length=1), db: Session = Depends(get_db)):
    return list(db.scalars(select(Chat).where(Chat.user_id == user_id).order_by(Chat.created_at.desc())))

@router.delete("/{chat_id}", status_code=204)
def delete_chat(chat_id: int, user_id: str = Query(min_length=1), db: Session = Depends(get_db)):
    chat = db.scalar(select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id))
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")
    db.delete(chat)
    db.commit()
    return None
