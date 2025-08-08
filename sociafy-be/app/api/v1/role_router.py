from fastapi import APIRouter
from app.db.supabase_client import supabase

router = APIRouter()
@router.get('/')
def get_roles():
    data = supabase.table("role").select("*").execute()
    return data.data
