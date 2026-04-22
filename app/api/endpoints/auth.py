from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
import httpx
from app.core.config import settings
from app.core.database import db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth import UserCreate, UserLogin, Token

router = APIRouter()

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"

@router.post("/register", response_model=Token)
async def register(user_in: UserCreate):
    # Check if user exists
    existing_user = await db.db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )
    
    # Create new user
    user_dict = user_in.dict()
    password = user_dict.pop("password")
    user_dict["hashed_password"] = get_password_hash(password)
    user_dict["created_at"] = datetime.utcnow()
    
    result = await db.db.users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    
    # Generate token
    access_token = create_access_token(subject=user_dict["_id"])
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user_dict["email"],
            "full_name": user_dict["full_name"],
            "id": user_dict["_id"],
            "default_mode": user_dict["default_mode"]
        }
    }

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin):
    user = await db.db.users.find_one({"email": user_in.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not verify_password(user_in.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Update mode if selected during login
    if user_in.selected_mode:
        await db.db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"default_mode": user_in.selected_mode}}
        )
        user["default_mode"] = user_in.selected_mode

    access_token = create_access_token(subject=str(user["_id"]))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "full_name": user["full_name"],
            "id": str(user["_id"]),
            "default_mode": user["default_mode"]
        }
    }

@router.get("/login/github")
async def login_github():
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub Client ID not configured.")
    
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "scope": "user repo",
        "prompt": "select_account",
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return RedirectResponse(f"{GITHUB_AUTHORIZE_URL}?{query_string}")

@router.get("/callback")
async def callback(code: str):
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="GitHub Credentials not configured.")

    async with httpx.AsyncClient() as client:
        # Exchange code for token
        response = await client.post(
            GITHUB_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )
        token_data = response.json()
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data.get("error_description"))

        access_token = token_data.get("access_token")
        
        # Get user info
        user_response = await client.get(
            GITHUB_USER_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_response.json()
        
        return RedirectResponse(
            f"http://localhost:3000/?token={access_token}&uid={user_info.get('id')}&user={user_info.get('login')}&avatar={user_info.get('avatar_url')}"
        )
