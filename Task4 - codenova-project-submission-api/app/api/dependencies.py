from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.admin import Admin
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException

# HTTP Bearer schemes
security_scheme = HTTPBearer(auto_error=True)
optional_security_scheme = HTTPBearer(auto_error=False)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    """
    Validate administrative JWT Bearer token and return authenticated Admin.
    Raises 401 Unauthorized if missing, expired, or invalid.
    """
    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authentication token is required")

    payload = decode_access_token(credentials.credentials)
    username: Optional[str] = payload.get("sub")
    if not username:
        raise UnauthorizedException("Token payload missing subject identifier")

    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        raise UnauthorizedException("Administrator account does not exist or has been disabled")

    return admin


def get_optional_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security_scheme),
    db: Session = Depends(get_db),
) -> Optional[Admin]:
    """
    Check if request has an administrative Bearer token.
    Returns Admin instance if authenticated; returns None for unauthenticated public requests.
    Raises 401 if a token was sent but is invalid or expired.
    """
    if not credentials or not credentials.credentials:
        return None

    payload = decode_access_token(credentials.credentials)
    username: Optional[str] = payload.get("sub")
    if not username:
        raise UnauthorizedException("Invalid token payload")

    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        raise UnauthorizedException("Administrator account does not exist")

    return admin

