from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException, Request
from app.db.supabase_client import supabase
from app.schemas.ai_flag import (
    AIFLagDisputeCreate, AIFLagDisputeResponse,
    ConfirmedStatusEnum
)

router = APIRouter()

@router.post("/", response_model=AIFLagDisputeResponse)
def create_dispute(request: Request, payload: AIFLagDisputeCreate):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    new_dispute = {
        "id": str(uuid.uuid4()),
        "ai_flag_id": payload.ai_flag_id,
        "user_id": user["id"],
        "reason": payload.reason,
        "status": ConfirmedStatusEnum.pending.value,
        "created_at": datetime.utcnow().isoformat()
    }

    supabase.table("ai_flag_disputes").insert(new_dispute).execute()
    return new_dispute

@router.put("/{dispute_id}")
def resolve_dispute(dispute_id: str, status: ConfirmedStatusEnum):
    res = supabase.table("ai_flag_disputes").select("*").eq("id", dispute_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Dispute not found")

    supabase.table("ai_flag_disputes").update({"status": status.value}).eq("id", dispute_id).execute()

    #  moderator confirm user right, has something wrong in AI d etect => delete record in ai_flag
    if status == ConfirmedStatusEnum.confirmed:
        ai_flag_id = res.data[0]["ai_flag_id"]
        supabase.table("ai_flag").delete().eq("id", ai_flag_id).execute()
        return {"message": "Dispute confirmed, AI flag deleted"}

    return {"message": f"Dispute updated to {status.value}"}