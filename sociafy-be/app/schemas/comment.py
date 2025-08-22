from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: str
    parent_comment_id: Optional[str] = None
    is_hided: bool = False

class CommentReply(CommentBase):
    post_id: str
    parent_comment_id: str
    is_hided: bool = False

class CommentResponse(CommentBase):
    id: str
    user_id: str
    post_id: str
    parent_comment_id: Optional[str] = None
    is_hided: bool
    created_at: datetime

    class Config:
        orm_mode = True