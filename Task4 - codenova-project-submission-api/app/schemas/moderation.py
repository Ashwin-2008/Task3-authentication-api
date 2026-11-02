from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models.submission import SubmissionStatus


class ModerationRequest(BaseModel):
    """Schema for administrator moderation actions."""

    status: str = Field(..., description="Target status: 'Pending', 'Approved', or 'Rejected'")
    feedback: Optional[str] = Field(None, max_length=2000, description="Optional feedback remarks from admin")

    model_config = ConfigDict(extra="forbid")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = {s.value for s in SubmissionStatus}
        if v not in valid_statuses:
            raise ValueError(
                f"Invalid status '{v}'. Allowed values are: {', '.join(sorted(valid_statuses))}"
            )
        return v

    @field_validator("feedback")
    @classmethod
    def strip_feedback(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return None

