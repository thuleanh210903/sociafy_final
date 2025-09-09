from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.share.enum.notification import NotificationType

class NotificationBase(BaseModel):
    user_id: str                
    type: NotificationType                    
    message: str
    post_id: Optional[str] = None
    comment_id: Optional[str] = None
    is_read: bool = False

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: str
    created_at: datetime