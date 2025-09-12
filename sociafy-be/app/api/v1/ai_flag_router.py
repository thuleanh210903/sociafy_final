from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException, Request
from app.db.supabase_client import supabase
from app.schemas.ai_flag import (
    AIFLagCreate, AIFLagResponse,
    AIFLagDisputeCreate, AIFLagDisputeResponse,
    ConfirmedStatusEnum
)

router = APIRouter()


@router.post('/add', response_model=AIFLagResponse)
def add_ai_flag(payload: AIFLagCreate):
    new_flag = {
        "id": str(uuid.uuid4()),
        "post_id": payload.post_id,
        "comment_id": payload.comment_id,
        "confidence": payload.confidence,
        "detected_label": payload.detected_label,
        "flagged_at": datetime.utcnow().isoformat(),
        "reviewed": False,
        "confirmed_status": ConfirmedStatusEnum.pending.value
    }

    supabase.table("ai_flag").insert(new_flag).execute()
    return new_flag

@router.get("/", response_model=list[AIFLagResponse])
def get_all_flags():
    res = supabase.table("ai_flag").select("*").execute()
    return res.data