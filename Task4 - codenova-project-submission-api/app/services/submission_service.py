from typing import Optional, Tuple, List
from sqlalchemy import or_, func, select
from sqlalchemy.orm import Session
from app.models.submission import Submission, SubmissionStatus
from app.schemas.submission import SubmissionCreate
from app.core.exceptions import NotFoundException, BadRequestException


class SubmissionService:
    """Service handling project submission operations."""

    @staticmethod
    def create_submission(db: Session, data: SubmissionCreate) -> Submission:
        """Create a new project submission with default Pending status."""
        submission = Submission(
            title=data.title,
            description=data.description,
            domain=data.domain,
            github_url=data.github_url,
            demo_url=data.demo_url,
            status=SubmissionStatus.PENDING.value,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return submission

    @staticmethod
    def get_submission_by_id(db: Session, submission_id: str, is_admin: bool = False) -> Submission:
        """
        Retrieve a single submission by its ID.
        Public users may only see Approved submissions; all others return 404 to avoid disclosure.
        """
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise NotFoundException("Submission not found")

        # Security check: Non-admin users cannot access non-approved submissions
        if not is_admin and submission.status != SubmissionStatus.APPROVED.value:
            raise NotFoundException("Submission not found")

        return submission

    @staticmethod
    def list_submissions(
        db: Session,
        is_admin: bool = False,
        search_query: Optional[str] = None,
        domain: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Submission], int]:
        """
        List, search, filter, and paginate submissions using database-level queries.
        Public users are strictly restricted to Approved submissions.
        """
        if page < 1:
            raise BadRequestException("Page number must be greater than or equal to 1")
        if limit < 1 or limit > 100:
            raise BadRequestException("Limit must be between 1 and 100")

        query = db.query(Submission)

        # 1. Status access control
        if not is_admin:
            query = query.filter(Submission.status == SubmissionStatus.APPROVED.value)
        else:
            if status:
                valid_statuses = {s.value for s in SubmissionStatus}
                if status not in valid_statuses:
                    raise BadRequestException(
                        f"Invalid status filter '{status}'. Allowed values: {', '.join(sorted(valid_statuses))}"
                    )
                query = query.filter(Submission.status == status)

        # 2. Search filter (q) across title and description
        if search_query and search_query.strip():
            term = f"%{search_query.strip()}%"
            query = query.filter(
                or_(
                    Submission.title.ilike(term),
                    Submission.description.ilike(term),
                )
            )

        # 3. Domain filter
        if domain and domain.strip():
            query = query.filter(func.lower(Submission.domain) == domain.strip().lower())

        # 4. Total count calculation before pagination
        count_stmt = select(func.count()).select_from(query.subquery())
        total_items = db.scalar(count_stmt) or 0

        # 5. Sorting
        sort_columns = {
            "created_at": Submission.created_at,
            "title": Submission.title,
            "domain": Submission.domain,
            "status": Submission.status,
            "updated_at": Submission.updated_at,
        }
        if sort_by not in sort_columns:
            raise BadRequestException(
                f"Unsupported sort_by field '{sort_by}'. Allowed: {', '.join(sorted(sort_columns.keys()))}"
            )

        col = sort_columns[sort_by]
        if sort_order.lower() == "asc":
            query = query.order_by(col.asc())
        elif sort_order.lower() == "desc":
            query = query.order_by(col.desc())
        else:
            raise BadRequestException(f"Unsupported sort_order '{sort_order}'. Allowed: 'asc', 'desc'")

        # 6. Database-level pagination
        offset_val = (page - 1) * limit
        items = query.offset(offset_val).limit(limit).all()

        return items, total_items

