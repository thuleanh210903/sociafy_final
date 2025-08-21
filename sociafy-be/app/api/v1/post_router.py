from datetime import datetime
from typing import List
import uuid
from fastapi import APIRouter, File, Form, Request, HTTPException, UploadFile
from app.db.supabase_client import supabase
from app.schemas.post import PostMessageResponse, PostCreate
from app.services.cloudinary_service import upload_cloudinary_image
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

