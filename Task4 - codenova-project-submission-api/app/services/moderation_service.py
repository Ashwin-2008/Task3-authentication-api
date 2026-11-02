from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.submission import Submission, SubmissionStatus
from app.schemas.moderation import ModerationRequest
from app.core.exceptions import NotFoundException, BadRequestException


class ModerationService:
    """Service handling moderation actions by administrators."""

    @staticmethod
    def moderate_submission(
        db: Session,
        submission_id: str,
        data: ModerationRequest,
    ) -> Submission:
        """
        Review, approve, or reject a project submission with feedback.
        Updates status, feedback, reviewed_at, and updated_at.
        """
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise NotFoundException(f"Submission with ID '{submission_id}' not found")

        valid_statuses = {s.value for s in SubmissionStatus}
        if data.status not in valid_statuses:
            raise BadRequestException(
                f"Invalid status '{data.status}'. Allowed statuses: {', '.join(sorted(valid_statuses))}"
            )

        now = datetime.now(timezone.utc)
        submission.status = data.status
        submission.feedback = data.feedback
        submission.reviewed_at = now
        submission.updated_at = now

        db.commit()
        db.refresh(submission)
        return submission

