from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Request
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

@router.put('/edit/{comment_id}')
def edit_comment(comment_id: str, comment: CommentCreate, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # check authorize
    existing = (
        supabase.table("comment")
        .select("id", "user_id")
        .eq("id", comment_id)
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Comment not found")

    if existing.data[0]["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not allowed to edit")
    
    # insert comment
    res = (supabase.table('comment').update({
        "content": comment.content,
    }).eq("id", comment_id).execute())

    return {"message": "Comment updated", "data": res.data}

@router.delete('/delete/{comment_id}')
def delete_comment(comment_id: str, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # check authorize
    existing = (
        supabase.table("comment")
        .select("id", "user_id")
        .eq("id", comment_id)
        .execute()
    )
    if not existing.data:
        raise HTTPException(status_code=404, detail="Comment not found")

    if existing.data[0]["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not allowed to delete")
    
    #delete
    supabase.table('comment').delete().eq("id", comment_id).execute()

    return {"message": "Comment deleted"}


@router.get('/list')
def  get_all_comments(post_id: str = Query(...)):
    # get comment by post id
    res = supabase.table('comment').select("*").eq("post_id", post_id).order("created_at", desc=False).execute()

    # divide 2 part: root comment and parent comment 
    comments = []
    for row in res.data:
        if not row["parent_comment_id"]:
            row["replies"] = [r for r in res.data if r["parent_comment_id"] == row["id"]]
            comments.append(row)
    
    return {"comments": comments}
