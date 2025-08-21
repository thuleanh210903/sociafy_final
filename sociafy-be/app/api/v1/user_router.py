from fastapi import APIRouter, HTTPException, Query
from app.db.supabase_client import supabase


router = APIRouter()

@router.get("/{user_id}")
def get_public_user(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    cursor: str | None = None
):
    user_record = (
        supabase.table("user")
        .select("id, firstName, lastName, avatar_url, birthOfDate")
        .eq("id", user_id)
        .execute()
    )
    if not user_record.data:
        raise HTTPException(status_code=404, detail="User not found")

    # Base query
    query = (
        supabase.table("post")
        .select("*")
        .eq("user_id", user_id)
        .eq("privacy", "public")
        .order("created_at", desc=True)
        .order("id", desc=True)
    )

    if cursor:
        cursor = cursor.strip()
        last_post_res = (
            supabase.table("post")
            .select("created_at")
            .eq("id", cursor)
            .execute()
        )
        if not last_post_res.data:
            raise HTTPException(status_code=400, detail="Invalid cursor id")
        cursor_dt = last_post_res.data[0]["created_at"]

        query = query.or_(
            f"created_at.lt.{cursor_dt},and(created_at.eq.{cursor_dt},id.lt.{cursor})"
        )

    posts_res = query.limit(limit).execute()
    posts = posts_res.data or []

    for post in posts:
        medias = supabase.table("media").select("*").eq("post_id", post["id"]).execute()
        post["media"] = medias.data

    return {
        "message": "Get public info successfully",
        "user": user_record.data[0],
        "posts": posts,
        "next_cursor": posts[-1]["id"] if posts else None,
        "has_more": len(posts) == limit
    }

