from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.chat import MessageCreateRequest, MessageResponse
from app.services.chat_service import (
    get_chat_messages,
    add_user_message,
)

router = APIRouter()

@router.post("/{chat_id}", response_model=MessageResponse, status_code=201)
def add_message(chat_id: UUID, payload: MessageCreateRequest, db: Session = Depends(get_db)):
    try:
        return add_user_message(
            db, chat_id=chat_id, user_id=payload.user_id, content=payload.content
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{chat_id}", response_model=list[MessageResponse])
def list_messages(chat_id: UUID, user_id: str = Query(min_length=1), db: Session = Depends(get_db)):
    try:
        return get_chat_messages(db, chat_id=chat_id, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))