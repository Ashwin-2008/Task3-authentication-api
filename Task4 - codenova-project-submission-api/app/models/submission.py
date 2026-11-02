import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Index
from app.db.base import Base


class SubmissionStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Submission(Base):
    """Database model for project submissions."""

    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    domain = Column(String(100), nullable=False, index=True)
    github_url = Column(String(500), nullable=False)
    demo_url = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default=SubmissionStatus.PENDING.value, index=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_submissions_status_domain", "status", "domain"),
        Index("idx_submissions_status_created_at", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Submission(id='{self.id}', title='{self.title[:30]}', status='{self.status}')>"

