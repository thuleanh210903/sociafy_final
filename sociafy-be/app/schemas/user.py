from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    avatar_url: str
    is_banned: bool
    birthOfDate: date
    isInfluencer: bool
    role_id: str

class UserCreate(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    birthOfDate: date
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str

class RegisterResponse(BaseModel):
    message: str
    user: UserResponse
    