from datetime import datetime
import uuid
from fastapi import APIRouter, Request, HTTPException
from app.db.supabase_client import supabase
from app.schemas.post import PostMessageResponse, PostCreate



router = APIRouter()

@router.get('/get-post')

@router.post('/add-post', response_model=PostMessageResponse)
def addPost(post: PostCreate, request: Request):
    # get user id
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    userId = user["id"]

    # prepare post data
    new_post = post.dict()
    new_post["id"] = str(uuid.uuid4())
    new_post["user_id"] = userId
    new_post["created_at"] = datetime.utcnow().isoformat()



    # insert supabase
    result = supabase.table("post").insert(new_post).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to insert post")

    # return message
    return {"message": "Post added successful", "post": result.data[0]}


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

