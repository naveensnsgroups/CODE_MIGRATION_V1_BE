from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
import httpx
from app.core.config import settings

router = APIRouter()

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"

@router.get("/login")
async def login():
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub Client ID not configured.")
    
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "scope": "user repo",
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
