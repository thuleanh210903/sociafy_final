from datetime import datetime
from typing import List
from fastapi import APIRouter, Body, HTTPException, Query, Request
from app.db.supabase_client import supabase

router = APIRouter()

@router.get('/')
def get_notifications(request: Request, limit: int = Query(20), offset: int = Query(0)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user["id"]

    res = supabase.table("notification").select("*").eq("user_id", user_id).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    return {"notifications": res.data}

@router.post("/mark-read")
def mark_notification_read(request: Request, notification_ids: List[str] = Body(...)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user["id"]

    supabase.table("notification").update({"is_read": True}) \
        .eq("user_id", user_id).in_("id", notification_ids).execute()

    return {"message": "Notifications marked as read"}