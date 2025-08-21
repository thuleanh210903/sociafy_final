from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReactionBase(BaseModel):
    type: str

class ReactionCreate(ReactionBase):
    post_id: Optional[str] = None
    comment_id: Optional[str] = None

class ReactionResponse(ReactionBase):
    id: str
    user_id: str
    post_id: Optional[str] = None
    comment_id: Optional[str] = None
    created_at: datetime 