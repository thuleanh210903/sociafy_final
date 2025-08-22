from pydantic import BaseModel


class SharePostRequest(BaseModel):
    post_id: str
    