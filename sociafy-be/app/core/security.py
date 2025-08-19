# JWT, OAuth2, Password ..
import os
import re
from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")

def validate_password_strength(password: str):
    "Require: At least 1 uppercase character, lowercase character, number and larger 8 character"

    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters" )
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    

def hash_password(password: str) -> str:
    validate_password_strength(password)
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
