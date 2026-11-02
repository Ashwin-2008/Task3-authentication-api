from datetime import timedelta
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.auth import AdminLogin, TokenResponse
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.core.exceptions import UnauthorizedException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Administrator login",
    description="Authenticate an administrator using username and password to obtain a signed JWT token.",
)
def login_for_access_token(
    credentials: AdminLogin,
    db: Session = Depends(get_db),
) -> TokenResponse:
    admin = db.query(Admin).filter(Admin.username == credentials.username).first()
    if not admin:
        raise UnauthorizedException("Invalid username or password")

    if not verify_password(credentials.password, admin.password_hash):
        raise UnauthorizedException("Invalid username or password")

    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username, "admin_id": admin.id},
        expires_delta=expires_delta,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

