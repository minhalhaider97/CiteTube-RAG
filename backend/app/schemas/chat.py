from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ChatCreateRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=36)
    video_id: int

class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: str
    video_id: int
    title: str
    created_at: datetime

class MessageCreateRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=36)
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=30000)

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    chat_id: int
    role: str
    content: str
    created_at: datetime
