from pydantic import BaseModel
from app.share.enum.privacy import PrivacyEnum


class PostBase(BaseModel): 
    content: str
    user_id: str
    privacy: str
    is_hided: bool

class PostCreate(BaseModel):
    content: str
    privacy: PrivacyEnum = PrivacyEnum.public

class PostCreateResponse(BaseModel):
    message: str