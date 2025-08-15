from fastapi import APIRouter, HTTPException
from app.db.supabase_client import supabase
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserResponse, RegisterResponse
import uuid
from datetime import date, datetime

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register(user: UserCreate):
    # check email exist
    existing = supabase.table("user").select("*").eq("email", user.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already existed")

    # get default role id is user
    role_data = supabase.table("role").select("id").execute()
    if not role_data.data or len(role_data.data) < 3:
        raise HTTPException(status_code=400, detail="Role data not valid")
    default_role_id = role_data.data[2]["id"]

    # create new user
    new_user = user.dict()
    new_user["id"] = str(uuid.uuid4())
    new_user["password"] = hash_password(user.password)
    new_user["role_id"] = default_role_id
    new_user["is_banned"] = False
    new_user["isInfluencer"] = False
    new_user["avatar_url"] = "text avatar"

    # Convert date to string ISO
    if isinstance(new_user.get("birthOfDate"), (datetime, date)):
        new_user["birthOfDate"] = new_user["birthOfDate"].isoformat()

    # Insert supabase
    result = supabase.table("user").insert(new_user).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to insert user")

    user_response = UserResponse(**{k: v for k, v in new_user.items() if k != "password"})
    return {
        "message": "Register successful",
        "user": user_response
    }
