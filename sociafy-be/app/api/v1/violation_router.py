from fastapi import APIRouter
from app.db.supabase_client import supabase

router = APIRouter()

@router.get("/")
def get_all_violations():
    res = supabase.table("violation").select("*").execute()
    return {
        "message": "Get all violations",
        "violations": res.data
    }


@router.get("/user/{user_id}")
def get_user_violations(user_id: str):

    res = supabase.table("violation").select("*").eq("user_id", user_id).execute()
    return {
        "message": f"Get violations for user {user_id}",
        "violations": res.data
    }
