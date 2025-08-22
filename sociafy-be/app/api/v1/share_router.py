from datetime import datetime
from fastapi import APIRouter, Body, HTTPException, Query, Request
from app.schemas.share import SharePostRequest
from app.db.supabase_client import supabase

router = APIRouter()

@router.post('/')
def share_post(request: Request, data: SharePostRequest = Body(...)):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = user["id"]

    # check post
    post = supabase.table('post').select("id").eq("id", data.post_id).execute()
    if not post.data:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # insert
    res = supabase.table('share').insert({
        "user_id": user_id,
        "post_id": data.post_id,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    return {"message": "Post shared successfully", "share": res.data}

@router.get('/count')
def get_share_count(post_id: str = Query(...)):
    # check post
    post = supabase.table("post").select("id").eq("id", post_id).execute()
    if not post.data:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # count share
    res = supabase.table('share').select("post_id", count="exact").eq("post_id", post_id).execute()

    return {"post_id": post_id, "share_count": res.count}
