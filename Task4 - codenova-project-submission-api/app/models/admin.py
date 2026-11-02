import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app.db.base import Base


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Admin(Base):
    """Database model for administrative users."""

    __tablename__ = "admins"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    def __repr__(self) -> str:
        return f"<Admin(id='{self.id}', username='{self.username}')>"

