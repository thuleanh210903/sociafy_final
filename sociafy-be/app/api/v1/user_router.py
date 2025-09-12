from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile
from app.db.supabase_client import supabase
from app.services.cloudinary_service import upload_cloudinary_image


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

@router.get('/all')
def get_all_users(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    userId = user["id"]
    user_record = (
        supabase.table('user').select('id, role_id').eq("id", userId).execute()       
		)
    if not user_record.data:
        raise HTTPException(status_code=404, detail="User not found")

    role_id = user_record.data[0]["role_id"]
    role_res = supabase.table("role").select("role_name").eq("id", role_id).execute()
    if not role_res.data:
        raise HTTPException(status_code=403, detail="Role not found")

    role_name = role_res.data[0]["role_name"]
    if role_name not in ["moderator", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users = (
        supabase.table("user")
        .select("id, firstName, lastName, avatar_url, birthOfDate, role_id")
        .execute()
    )
    return {
        "message": "Get all users successfully",
        "users": users.data or []
    }

@router.post("/update-avatar")
async def update_avatar(
    request: Request,
    avatar: UploadFile = File(...),
):
    # get user from session
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    userId = user["id"]

    # Upload avatar Cloudinary
    try:
        uploaded = upload_cloudinary_image(
            file=avatar,
            key="avatar",
            user_id=userId
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Update avatar_url in supabase
    result = (
        supabase.table("user")
        .update({"avatar_url": uploaded["url"]})
        .eq("id", userId)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update avatar")

    return {
        "message": "Avatar updated successfully",
        "user": result.data[0]
    }

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from app.db.supabase_client import supabase
from app.services.cloudinary_service import upload_cloudinary_image

router = APIRouter()


@router.put("/me")
async def update_my_info(
    request: Request,
    firstName: str = Form(None),
    lastName: str = Form(None),
    birthOfDate: str = Form(None),
    avatar: UploadFile = File(None),
):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    userId = user["id"]

    update_data = {}

    if firstName is not None:
        update_data["firstName"] = firstName
    if lastName is not None:
        update_data["lastName"] = lastName
    if birthOfDate is not None:
        update_data["birthOfDate"] = birthOfDate

    if avatar:
        try:
            uploaded = upload_cloudinary_image(
                file=avatar,
                key="avatar",
                user_id=userId
            )
            update_data["avatar_url"] = uploaded["url"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = (
        supabase.table("user")
        .update(update_data)
        .eq("id", userId)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update user info")

    return {
        "message": "User info updated successfully",
        "user": result.data[0]
    }