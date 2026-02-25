from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "viewer"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None

class UserInDB(UserBase):
    hashed_password: str

class User(UserBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
