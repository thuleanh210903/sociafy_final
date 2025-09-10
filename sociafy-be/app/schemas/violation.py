from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ViolationBase(BaseModel):
    userId: str
    postId: Optional[str] = None
    commentId: Optional[str] = None
    reason: str
    strike_count: int = 1


class ViolationResponse(BaseModel):
    id: str
    userId: str
    postId: Optional[str] = None
    commentId: Optional[str] = None
    reason: str
    strike_count: int
    created_at: datetime


class ViolationMessageResponse(BaseModel):
    message: str
