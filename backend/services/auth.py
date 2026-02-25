from datetime import datetime, timedelta
from typing import Optional
import logging
from jose import jwt, JWTError
from passlib.context import CryptContext
from ..config import get_settings
from ..db import get_db

logger = logging.getLogger(__name__)
settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate a bcrypt hash of a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def get_user_by_username(username: str):
    """Fetch a user from the database by username."""
    db = get_db()
    user = db["users"].find_one({"username": username})
    if user:
        user["_id"] = str(user["_id"])
    return user

def authenticate_user(username: str, password: str):
    """Authenticate a user by username and password."""
    user = get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user
