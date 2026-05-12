from typing import Annotated

import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.dependencies import get_db_session
from app.schemas.auth import OAuthTokenResponse, Token
from app.services.auth_service import AuthService

router = APIRouter()


def _configure_oauth() -> OAuth | None:
    settings = get_settings()
    if not settings.oauth_google_client_id or not settings.oauth_google_client_secret:
        return None
    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=settings.oauth_google_client_id,
        client_secret=settings.oauth_google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    return oauth


@router.post("/token", response_model=Token)
async def login_access_token(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    auth_service = AuthService(session)
    user = await auth_service.authenticate(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = await auth_service.issue_token_for_user(user)
    return Token(access_token=token)


@router.get("/oauth/google/login")
async def oauth_google_login(request: Request) -> RedirectResponse:
    settings = get_settings()
    oauth = _configure_oauth()
    if oauth is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured",
        )
    redirect_uri = f"{settings.oauth_redirect_base_url.rstrip('/')}/api/v1/auth/oauth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/oauth/google/callback", response_model=OAuthTokenResponse)
async def oauth_google_callback(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> OAuthTokenResponse:
    oauth = _configure_oauth()
    if oauth is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured",
        )
    tok = await oauth.google.authorize_access_token(request)
    userinfo = tok.get("userinfo") or {}
    email = userinfo.get("email")
    if not email and tok.get("access_token"):
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            resp = await http_client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {tok['access_token']}"},
            )
            resp.raise_for_status()
            userinfo = resp.json()
            email = userinfo.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not returned by provider",
        )

    auth_service = AuthService(session)
    user = await auth_service.get_or_create_google_oauth_user(
        email=email, full_name=userinfo.get("name")
    )
    jwt_token = await auth_service.issue_token_for_user(user)
    return OAuthTokenResponse(access_token=jwt_token)
