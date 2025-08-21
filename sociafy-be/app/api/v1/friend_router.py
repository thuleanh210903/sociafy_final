from datetime import datetime
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

    friendship = supabase.table("friend").select("*").or_(
        f"(user_id.eq.{user_id},friend_id.eq.{friend_id}),"
        f"(user_id.eq.{friend_id},friend_id.eq.{user_id})"
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


@router.post("/accept-friend/{user_id}")
def accept_friend(user_id: str, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    friend_id = user["id"]

    friendship = supabase.table("friend").select("*") \
        .eq("user_id", user_id).eq("friend_id", friend_id).execute()
    
    if not friendship.data:
        raise HTTPException(status_code=404, detail="Friend request not found")

    record = friendship.data[0]
    if record["status"]:
        raise HTTPException(status_code=400, detail="Already friends")
    
    supabase.table('friend').update({
        "status": True
    }).eq("user_id", user_id).eq("friend_id", friend_id).execute()

    return {"message": "Friend request accepted successfully"}


@router.post("/unfriend/{friend_id}")
def unfriend(friend_id: str, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user["id"]

    friendship = supabase.table("friend").select("*").or_(
    f"and(user_id.eq.{user_id},friend_id.eq.{friend_id}),"
    f"and(user_id.eq.{friend_id},friend_id.eq.{user_id})"
).execute()

    if not friendship.data:
        raise HTTPException(status_code=404, detail="Friendship not found")

    record = friendship.data[0]
    if not record["status"]:
        raise HTTPException(status_code=400, detail="Not friends yet")

    if record["user_id"] == user_id and record["friend_id"] == friend_id:
        supabase.table("friend").update({"status": False}) \
            .eq("user_id", user_id).eq("friend_id", friend_id).execute()
    else:
        supabase.table("friend").update({"status": False}) \
            .eq("user_id", friend_id).eq("friend_id", user_id).execute()

    return {"message": "Unfriended successfully"}
