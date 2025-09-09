from enum import Enum

class NotificationType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    REPLY = "reply"
    SHARE = "share"
    FRIEND_REQUEST = "friend_request"