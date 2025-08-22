from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from app.schemas.comment import CommentCreate
from app.db.supabase_client import supabase

router = APIRouter()

@router.post('/add')
def add_comment(request: Request, comment: CommentCreate):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user["id"]

    # check post exist
    post = supabase.table('post').select("id").eq("id", comment.post_id).execute()
    if not post.data:
        raise HTTPException(status_code=404, detail="Post not found")

    # if has parrent, check parrent
    if comment.parent_comment_id:
        parent = supabase.table('comment').select('id').eq('id', comment.parent_comment_id).execute()
        if not parent.data:
            raise HTTPException(status_code=404, detail="Parent comment not found")

    # insert comment table
    res = supabase.table('comment').insert({
        "content": comment.content,
        "post_id": comment.post_id,
        "user_id": user_id,
        "parent_comment_id": comment.parent_comment_id,
        "is_hided": comment.is_hided,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    return {"Message": "Comment added", "data": res.data}