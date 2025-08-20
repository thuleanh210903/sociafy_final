# app/api/v1/auth_router.py
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from app.db.supabase_client import supabase
from app.core.security import hash_password, verify_password
from app.core.email_utils import send_otp
from app.schemas.user import UserCreate, UserResponse, RegisterResponse, VerifyOTPRequest, UserLogin
from datetime import datetime, date, timedelta
import uuid
import random


router = APIRouter()

OTP_EXPIRE_MINUTES = 10
OTP_MAX_SEND = 3

def generate_otp():
    return str(random.randint(100000, 999999))

# register endpoint
@router.post("/register", response_model=RegisterResponse)
def register(user: UserCreate):
    # check email exist
    existing = supabase.table("user").select("*").eq("email", user.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already existed")

    # get default role id
    role_data = supabase.table("role").select("id").execute()
    if not role_data.data or len(role_data.data) < 3:
        raise HTTPException(status_code=400, detail="Role data not valid")
    
    default_role_id = role_data.data[2]["id"]

    # prepare new user data
    new_user = user.dict()
    new_user["id"] = str(uuid.uuid4())
    new_user["password"] = hash_password(user.password)
    new_user["role_id"] = default_role_id
    new_user["is_banned"] = False
    new_user["isInfluencer"] = False
    new_user["avatar_url"] = "text avatar"
    new_user["is_verified"] = False

    # convert date to ISO string
    birth = new_user.get("birthOfDate")
    if isinstance(birth, (date, datetime)):
        new_user["birthOfDate"] = birth.isoformat()

    # generate and store OTP
    otp = generate_otp()
    new_user["otp_code"] = otp
    new_user["otp_expires_at"] = (datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)).isoformat()
    new_user["otp_attempts"] = 0

    # insert into Supabase
    result = supabase.table("user").insert(new_user).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to insert user")

    # send OTP email
    send_otp(user.email, otp)

    user_response = UserResponse(**{k: v for k, v in new_user.items() if k != "password"})
    return {"message": "Register successful. OTP sent to email.", "user": user_response}


# verify otp
@router.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest):
    user_record = supabase.table("user").select("*").eq("email", data.email).execute()
    if not user_record.data:
        raise HTTPException(status_code=400, detail="No OTP found for this email")

    user = user_record.dthêata[0]

    if user["is_verified"]:
        return {"message": "Email already verified"}

    if user.get("otp_attempts", 0) > OTP_MAX_SEND:
        raise HTTPException(status_code=429, detail="Max OTP attempts reached")
    
    if user["otp_code"] != data.otp_code:
        raise HTTPException(status_code=400, detail="OTP is incorrect")
    
    if datetime.utcnow() > datetime.fromisoformat(user["otp_expires_at"]):
        raise HTTPException(status_code=400, detail="OTP expired")
    
    supabase.table("user").update({
        "is_verified": True,
        "otp_code": None,
        "otp_expires_at": None,
        "otp_attempts": 0
    }).eq("email", data.email).execute()

    return {"message": "Email verified successfully"}


# resend otp
@router.post("/resend-otp")
def resend_otp(email: str):
    user_record = supabase.table("user").select("*").eq("email", email).execute()
    if not user_record.data:
        raise HTTPException(status_code=400, detail="User not found")
    
    user = user_record.data[0]

    if user.get("otp_attempts", 0) >= OTP_MAX_SEND:
        raise HTTPException(status_code=429, detail="Max OTP send attempts reached. Try later.")

    otp = generate_otp()
    send_count = (user.get("otp_attempts", 0) + 1)

    supabase.table("user").update({
        "otp_code": otp,
        "otp_expires_at": (datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)).isoformat(),
        "otp_attempts": send_count
    }).eq("email", email).execute()

    send_otp(email, otp)
    return {"message": f"OTP sent successfully. Attempt {send_count}"}


#Login
@router.post('/login')
def login(request: Request, body: UserLogin):
    user_record = supabase.table("user").select("*").eq("email", body.email).execute()

    if not user_record.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = user_record.data[0]

    if not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.get("is_verified", False):
        raise HTTPException(status_code=403, detail="Account is banned")
    
    request.session["user"] = {
        "id": user["id"],
        "email": user["email"],
        "firstName": user["firstName"],
        "lastName": user["lastName"],
        "avatar_url": user["avatar_url"],
        "birthOfDate": user["birthOfDate"],
        "isInfluencer": user["isInfluencer"],
        "role_id": user["role_id"],
    }
    return {"message": "Login successful", "user": {"email": user["email"], "firstName": user["firstName"],"lastName": user["lastName"],"avatar_url": user["avatar_url"],"birthOfDate": user["birthOfDate"], "role_id": user["role_id"]}}

#logout
@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logout successful"}

# info
@router.get("/me")
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"user": user}