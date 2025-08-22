from datetime import datetime
from typing import List, Optional
import uuid
from fastapi import APIRouter, File, Form, Query, Request, HTTPException, UploadFile
from app.db.supabase_client import supabase
from app.schemas.post import PostMessageResponse
from app.services.cloudinary_service import upload_cloudinary_image, delete_cloudinary_asset
from app.share.enum.privacy import PrivacyEnum
router = APIRouter()

@router.get('/get-post-me')
def getPostOfMe(request: Request):
    # get user id
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    userId = user["id"]
    # get  all post of current user
    posts = supabase.table("post").select("*").eq("user_id", userId).execute()

    if not posts.data:
        return {"message": "No posts found", "posts": []}
    
    return {"message": "Get posts successful", "posts": posts.data}

@router.get("/feed")
def get_feed(
    request: Request,
    limit: int = Query(2, ge=1, le=10),
    cursor: str | None = None  
):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user["id"]

    friends_res = (
        supabase.table("friend")
        .select("*")
        .or_(f"user_id.eq.{user_id},friend_id.eq.{user_id}")
        .eq("status", True)
        .execute()
    )

    friend_ids = {f["friend_id"] if f["user_id"] == user_id else f["user_id"] for f in friends_res.data}
    all_ids = list(friend_ids) + [user_id]

    # base query
    query = (
        supabase.table("post")
        .select("*")
        .in_("user_id", all_ids)
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

    next_cursor = posts[-1]["id"] if posts else None

    return {
        "data": posts,
        "next_cursor": next_cursor,
        "has_more": len(posts) == limit
    }



@router.post('/add-post', response_model=PostMessageResponse)
async def addPost(
    request: Request,
    content: str = Form(...),
    privacy: PrivacyEnum = Form(PrivacyEnum.public),
    files: List[UploadFile] = File(None)
):
    # get user id
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    userId = user["id"]

    # prepare post data
    new_post = {
        "id": str(uuid.uuid4()),
        "content": content,
        "user_id": userId,
        "privacy": privacy.value,
        "is_hided": False,
        "created_at": datetime.utcnow().isoformat()
    }

    # insert supabase
    result = supabase.table("post").insert(new_post).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to insert post")
    
    post_id = new_post["id"]

    media_records = []
    if files:
        for f in files:
            uploaded = upload_cloudinary_image(file=f, key='post', user_id=userId, post_id=post_id)
            media = {
                "id": str(uuid.uuid4()),
                "post_id": post_id,
                "media_url": uploaded["url"],
                "media_type": uploaded["resource_type"],
            }
            supabase.table("media").insert(media).execute()
            media_records.append(media)

    # return message
    return {"message": "Post added successful", "post": result.data[0], "media": media_records}

@router.put("/edit-post/{post_id}", response_model=PostMessageResponse)
async def editPost(
    post_id: str,
    request: Request,
    content: Optional[str] = Form(None),
    privacy: Optional[PrivacyEnum] = Form(None),
    files: List[UploadFile] = File(None),
    media_ids_to_delete: Optional[List[str]] = Form(None)
):
    # check login
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    userId = user["id"]

    # find post
    post_record = supabase.table("post").select("*").eq("id", post_id).execute()
    if not post_record.data:
        raise HTTPException(status_code=404, detail="Post not found")

    post = post_record.data[0]
    if post["user_id"] != userId:
        raise HTTPException(status_code=403, detail="You are not allowed to edit this post")

    # update post fields if provided
    update_data = {}
    if content is not None:
        update_data["content"] = content
    if privacy is not None:
        update_data["privacy"] = privacy.value

    if update_data:
        supabase.table("post").update(update_data).eq("id", post_id).execute()

    # delete selected media
    if media_ids_to_delete:
        for media_id in media_ids_to_delete:
            supabase.table("media").delete().eq("id", media_id).execute()

    # add new media
    media_records = []
    if files:
        for f in files:
            uploaded = upload_cloudinary_image(file=f, key='post', user_id=userId, post_id=post_id)
            media = {
                "id": str(uuid.uuid4()),
                "post_id": post_id,
                "media_url": uploaded["url"],
                "media_type": uploaded["resource_type"],
            }
            supabase.table("media").insert(media).execute()
            media_records.append(media)

    return {
        "message": "Post updated successfully",
        "post": {**post, **update_data},
        "media_added": media_records,
        "media_deleted": media_ids_to_delete or []
    }

@router.delete("/media/{media_id}")
def delete_media(media_id: str, request: Request):
    # check login
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    userId = user["id"]

    # find media record
    media_record = supabase.table("media").select("*").eq("id", media_id).execute()
    if not media_record.data:
        raise HTTPException(status_code=404, detail="Media not found")

    media = media_record.data[0]

    # find post to check owner
    post_record = supabase.table("post").select("user_id").eq("id", media["post_id"]).execute()
    if not post_record.data:
        raise HTTPException(status_code=404, detail="Post not found")

    post = post_record.data[0]
    if post["user_id"] != userId:
        raise HTTPException(status_code=403, detail="You are not allowed to delete this media")

    # delete media in DB
    supabase.table("media").delete().eq("id", media_id).execute()

    # optional: delete in Cloudinary too
    try:
        delete_cloudinary_asset(media["media_url"])
    except Exception:
        pass  # ignore if cloudinary delete fails

    return {"message": "Media deleted successfully", "media_id": media_id}


@router.delete('/delete-post/{post_id}', response_model=PostMessageResponse)
def deletePost(post_id: str, request: Request):
    # logged in
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    userId = user["id"]

    #find post
    post_record = supabase.table('post').select("*").eq("id", post_id).execute()
    if not post_record.data:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # authorize: post of user ?
    post = post_record.data[0]
    if post["user_id"] != userId:
        raise HTTPException(status_code=403, detail="You are not allowed to delete this post")
    
    # delete post
    supabase.table('post').delete().eq("id", post_id).execute()

    return {"message": "Post deleted successfully"}

