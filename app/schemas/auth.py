from pydantic import BaseModel, Field

from app.schemas.person import PersonPublic


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, examples=["john"])
    password: str = Field(..., min_length=1, max_length=128, examples=["2580"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    remember_username_days: int
    user: PersonPublic


class MeResponse(PersonPublic):
    pass
