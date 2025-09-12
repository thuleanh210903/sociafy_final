from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class ConfirmedStatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    rejected = "rejected"


class AIFLagBase(BaseModel):
    confidence: float
    detected_label: str
    post_id: Optional[str] = None
    comment_id: Optional[str] = None


class AIFLagCreate(AIFLagBase):
    pass


class AIFLagResponse(AIFLagBase):
    id: str
    flagged_at: datetime
    reviewed: bool
    confirmed_status: ConfirmedStatusEnum

    class Config:
        orm_mode = True


class AIFLagDisputeBase(BaseModel):
    ai_flag_id: str
    reason: str


class AIFLagDisputeCreate(AIFLagDisputeBase):
    pass


class AIFLagDisputeResponse(AIFLagDisputeBase):
    id: str
    user_id: str
    created_at: datetime
    status: ConfirmedStatusEnum

    class Config:
        orm_mode = True
