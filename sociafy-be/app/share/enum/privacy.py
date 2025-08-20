from enum import Enum


class PrivacyEnum(str, Enum):
    public = "public"
    only_friend = "only_friend"
    private = "private"
    