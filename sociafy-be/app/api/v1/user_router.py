from fastapi import APIRouter, HTTPException
from app.db.supabase_client import supabase


router = APIRouter()

@router.get('/{user_id}')
def get_public_user(user_id: str):
    user_record = supabase.table("user").select("id, firstName, lastName, avatar_url, birthOfDate").eq("id", user_id).execute()

    if not user_record.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    public_user = user_record.data

    #get post only public
    posts = supabase.table("post").select("*").eq("user_id", user_id).eq("privacy", "public").execute()

    posts_with_media = []
    for post in posts.data:
        medias = supabase.table("media").select("*").eq("post_id", post["id"]).execute()
        post["media"] = medias.data
        posts_with_media.append(post)

    return {
        "message": "Get public info successfully",
        "user": public_user,
        "posts": posts_with_media
    }