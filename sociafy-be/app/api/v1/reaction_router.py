from typing import Optional
from fastapi import APIRouter, Body, HTTPException, Request
from app.schemas.react import ReactionBase, ReactionCreate, ReactionResponse
from app.db.supabase_client import supabase

router = APIRouter()

@router.post("/add")
def react(reaction: ReactionCreate, request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user["id"]

    # check target 
    if reaction.post_id:
        post = supabase.table("post").select("id").eq("id", reaction.post_id).execute()
        if not post.data:
            raise HTTPException(status_code=404, detail="Post not found")
    if reaction.comment_id:
        comment = supabase.table("comment").select("id").eq("id", reaction.comment_id).execute()
        if not comment.data:
            raise HTTPException(status_code=404, detail="Comment not found")

    # check if reaction already exists
    query = supabase.table("reaction").select("*").eq("user_id", user_id)
    if reaction.post_id:
        query = query.eq("post_id", reaction.post_id)
    if reaction.comment_id:
        query = query.eq("comment_id", reaction.comment_id)

    existing = query.execute()

    if existing.data:
        # update reaction 
        res = (
            supabase.table("reaction")
            .update({"type": reaction.type})
            .eq("id", existing.data[0]["id"])
            .execute()
        )
    else:
        # insert new
        res = supabase.table("reaction").insert({
            "user_id": user_id,
            "post_id": reaction.post_id,
            "comment_id": reaction.comment_id,
            "type": reaction.type
        }).execute()

    return {"message": "Reacted successfully"}


@router.delete('/unreact')
def unreact(
    request: Request,
    post_id: Optional[str] = Body(None),
    comment_id: Optional[str] = Body(None)
):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = user["id"]

    if not post_id and not comment_id:
        raise HTTPException(status_code=400, detail="Must provide post_id or comment_id")
    
    query = supabase.table('reaction').delete().eq('user_id', user_id)
    if post_id:
        query = query.eq('post_id', post_id)
    if comment_id:
        query = query.eq('comment_id', comment_id)
    query.execute()

    return {"message": "Reaction removed"}

@router.get('/all')
def get_reactions(
    post_id: Optional[str] = None,
    comment_id: Optional[str] = None
):
    if not post_id and not comment_id:
        raise HTTPException(status_code=400, detail="Must provide post_id or comment_id")
    query = supabase.table("reaction").select("id, user_id, type, created_at")

    if post_id:
        query = query.eq('post_id', post_id)
    if comment_id:
        query = query.eq('comment_id', comment_id)
    res = query.execute()
    
    summary = {}
    for row in res.data:
        t = row["type"]
        summary[t] = summary.get(t, 0) + 1

    return {"data": res.data, "summary": summary}
