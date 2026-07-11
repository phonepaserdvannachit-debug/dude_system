from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.core.database import get_db
from app.models.person import Person
from app.schemas.auth import LoginRequest, MeResponse, PinChangeRequest, PinVerifyRequest, PinVerifyResponse, ProfileUpdateRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    auth_service = AuthService(db)
    person = auth_service.authenticate(payload.username, payload.password)
    token = auth_service.create_login_token(person)

    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        remember_username_days=settings.REMEMBER_USERNAME_DAYS,
        user=person,
    )


@router.get("/me", response_model=MeResponse)
def get_me(current_user: Person = Depends(get_current_user)) -> Person:
    return current_user


@router.patch("/me", response_model=MeResponse)
def update_me(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> Person:
    current_user.name = payload.name.strip()
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/pin/verify", response_model=PinVerifyResponse)
def verify_pin(
    payload: PinVerifyRequest,
    current_user: Person = Depends(get_current_user),
) -> PinVerifyResponse:
    return PinVerifyResponse(
        verified=verify_password(payload.password, current_user.password_hash)
    )


@router.patch("/me/pin", response_model=PinVerifyResponse)
def change_pin(
    payload: PinChangeRequest,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> PinVerifyResponse:
    if not verify_password(payload.current_password, current_user.password_hash):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current PIN is incorrect",
        )

    current_user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return PinVerifyResponse(verified=True)
