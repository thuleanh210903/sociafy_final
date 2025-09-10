from enum import Enum

class ReportStatusEnum(str, Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"
