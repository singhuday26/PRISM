from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from ..schemas.user import Token, User, UserCreate, TokenData
from ..services import auth as auth_service
from ..config import get_settings
from ..db import get_db

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get the current authenticated user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    user = auth_service.get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=User)
async def register_user(user_in: UserCreate):
    """Register a new user."""
    if auth_service.get_user_by_username(user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db = get_db()
    if db["users"].find_one({"email": user_in.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user_in.model_dump()
    password = user_dict.pop("password")
    user_dict["hashed_password"] = auth_service.get_password_hash(password)
    
    result = db["users"].insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    return user_dict

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Obtain a JWT access token using username and password."""
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user["username"], "role": user.get("role", "viewer")},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get profile of current authenticated user."""
    # Ensure current_user dict has 'id' field for the response model
    if "_id" in current_user and "id" not in current_user:
        current_user["id"] = str(current_user["_id"])
    return current_user
