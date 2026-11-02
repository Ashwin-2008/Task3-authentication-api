from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AdminLogin(BaseModel):
    """Schema for administrator login credentials."""

    username: str = Field(..., min_length=3, max_length=50, description="Admin username")
    password: str = Field(..., min_length=6, max_length=128, description="Admin password")

    model_config = ConfigDict(extra="forbid")


class TokenResponse(BaseModel):
    """Schema for returning JWT access token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AdminResponse(BaseModel):
    """Schema for administrative user public information."""

    id: str
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

