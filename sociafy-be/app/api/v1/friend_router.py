from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException, Request
from app.db.supabase_client import supabase

router = APIRouter()

@router.post("/add-friend/{friend_id}")
def add_friend(friend_id: str, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user["id"]

    if user_id == friend_id:
        raise HTTPException(status_code=400, detail="Cannot add yourself")

    # check exist
    friendship = supabase.table("friend").select("*").or_(
    f"user_id.eq.{user_id},and(friend_id.eq.{friend_id}),or(user_id.eq.{friend_id},and(friend_id.eq.{user_id}))"
).execute()

    if friendship.data:
        raise HTTPException(status_code=400, detail="Friend request already exists or already friends")

    new_friend_request = {
        "user_id": user_id,
        "friend_id": friend_id,
        "status": False,
        "requested_at": datetime.utcnow().isoformat(),
    }
    supabase.table("friend").insert(new_friend_request).execute()

    return {"message": "Friend request sent successfully", "friendship": new_friend_request}