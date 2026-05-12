from pydantic import BaseModel, EmailStr


class TokenRequest(BaseModel):
    username: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OAuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
