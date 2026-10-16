import uuid
from typing import Any, List, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.chat import Chat, Message
from app.db.models.video import Video
from app.rag.chain import run_rag_chain


def create_chat_session(
    db: Session,
    user_id: uuid.UUID | str,
    video_id: uuid.UUID | str
) -> Chat:
    """
    Creates a new Chat session linked to a specific user and ingested video.
    """
    # Ensure IDs are UUID objects
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)
    if isinstance(video_id, str):
        video_id = uuid.UUID(video_id)

    # 1. Verify that the video exists
    video = db.get(Video, video_id)
    if not video:
        raise ValueError("Video not found.")

    # 2. Check ingestion status if your model tracks it (e.g. video.status)
    if hasattr(video, "status") and video.status != "completed":
        raise ValueError("Video ingestion is not completed yet.")

    # 3. Create chat session using the video's title
    chat = Chat(
        user_id=user_id,
        video_id=video.id,
        title=getattr(video, "title", "Untitled Video Chat")
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_user_chats(db: Session, user_id: uuid.UUID | str) -> List[Chat]:
    """
    Retrieves all active chat sessions for a specific user ordered by newest first.
    """
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)

    stmt = select(Chat).where(Chat.user_id == user_id).order_by(Chat.updated_at.desc())
    return list(db.scalars(stmt).all())


def get_chat_by_id(
    db: Session,
    chat_id: uuid.UUID | str,
    user_id: uuid.UUID | str
) -> Chat | None:
    """
    Retrieves a single chat session owned by a specific user.
    """
    if isinstance(chat_id, str):
        chat_id = uuid.UUID(chat_id)
    if isinstance(user_id, str):
        user_id = uuid.UUID(user_id)

    stmt = select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
    return db.scalar(stmt)


def delete_chat_session(
    db: Session,
    chat_id: uuid.UUID | str,
    user_id: uuid.UUID | str
) -> bool:
    """
    Deletes a chat session and all cascading messages.
    """
    chat = get_chat_by_id(db, chat_id=chat_id, user_id=user_id)
    if not chat:
        return False

    db.delete(chat)
    db.commit()
    return True


def get_chat_messages(
    db: Session,
    chat_id: uuid.UUID | str,
    user_id: uuid.UUID | str
) -> List[Message]:
    """
    Fetches all messages for a verified chat session ordered chronologically.
    """
    chat = get_chat_by_id(db, chat_id=chat_id, user_id=user_id)
    if not chat:
        raise ValueError("Chat session not found or access denied.")

    stmt = select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at.asc())
    return list(db.scalars(stmt).all())


def add_user_message(
    db: Session,
    chat_id: uuid.UUID | str,
    user_id: uuid.UUID | str,
    content: str
) -> Message:
    """
    Adds a raw user message to the chat session.
    """
    chat = get_chat_by_id(db, chat_id=chat_id, user_id=user_id)
    if not chat:
        raise ValueError("Chat session not found or access denied.")

    user_msg = Message(
        chat_id=chat.id,
        role="user",
        content=content,
        message_metadata={}
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    return user_msg


def process_rag_query(
    db: Session,
    chat_id: uuid.UUID | str,
    user_id: uuid.UUID | str,
    query: str
) -> Tuple[Message, Message, dict[str, Any]]:
    """
    Executes the full RAG workflow:
    1. Persists the user query as a Message.
    2. Runs `run_rag_chain(db, video_id, query)`.
    3. Persists the AI response with citation metadata in message_metadata.
    """
    chat = get_chat_by_id(db, chat_id=chat_id, user_id=user_id)
    if not chat:
        raise ValueError("Chat session not found or access denied.")

    # 1. Store User Message
    user_message = Message(
        chat_id=chat.id,
        role="user",
        content=query,
        message_metadata={}
    )
    db.add(user_message)
    db.commit()

    # 2. Execute RAG Chain against the video ID attached to the chat
    rag_result = run_rag_chain(db, video_id=chat.video_id, query=query)
    answer = rag_result.get("answer", "")
    citations = rag_result.get("citations", [])

    # 3. Store Assistant Message with Citations in `message_metadata`
    assistant_message = Message(
        chat_id=chat.id,
        role="assistant",
        content=answer,
        message_metadata={"citations": citations}
    )
    db.add(assistant_message)
    db.commit()

    db.refresh(user_message)
    db.refresh(assistant_message)

    return user_message, assistant_message, rag_result