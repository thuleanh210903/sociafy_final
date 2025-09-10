from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.share.enum.report_status import ReportStatusEnum


class ReportBase(BaseModel):
    reporterId: str
    postId: Optional[str] = None
    commentId: Optional[str] = None
    reason: str
    status: str = ReportStatusEnum.pending


class ReportCreate(BaseModel):
    post_id: Optional[str] = None
    comment_id: Optional[str] = None
    reason: str

class ReportUpdateStatus(BaseModel):
    status: ReportStatusEnum

class ReportResponse(BaseModel):
    id: str
    reporterId: str
    postId: Optional[str] = None
    commentId: Optional[str] = None
    reason: str
    status: str
    created_at: datetime


class ReportMessageResponse(BaseModel):
    message: str
