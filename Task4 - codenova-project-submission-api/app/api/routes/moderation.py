from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.dependencies import get_current_admin
from app.models.admin import Admin
from app.schemas.moderation import ModerationRequest
from app.schemas.submission import (
    SubmissionResponse,
    SubmissionListResponse,
    PaginationMetadata,
)
from app.services.moderation_service import ModerationService
from app.services.submission_service import SubmissionService

router = APIRouter(prefix="/admin/submissions", tags=["Administration & Moderation"])


@router.patch(
    "/{submission_id}/moderation",
    response_model=SubmissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Moderate a project submission (PATCH)",
    description="Update submission status ('Pending', 'Approved', 'Rejected') and record administrator feedback.",
)
@router.post(
    "/{submission_id}/moderation",
    response_model=SubmissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Moderate a project submission (POST)",
    description="Update submission status ('Pending', 'Approved', 'Rejected') and record administrator feedback.",
)
def moderate_submission(
    submission_id: str,
    moderation_in: ModerationRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    submission = ModerationService.moderate_submission(
        db=db,
        submission_id=submission_id,
        data=moderation_in,
    )
    return submission


@router.get(
    "",
    response_model=SubmissionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Administrative submission list",
    description="List and filter submissions across all statuses (Pending, Approved, Rejected) for administrators.",
)
def list_admin_submissions(
    q: Optional[str] = Query(None, description="Search keyword in title or description"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    status: Optional[str] = Query(None, description="Filter by status (Pending, Approved, Rejected)"),
    page: int = Query(1, ge=1, description="Page number, 1-indexed"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> SubmissionListResponse:
    items, total_items = SubmissionService.list_submissions(
        db=db,
        is_admin=True,
        search_query=q,
        domain=domain,
        status=status,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    pagination = PaginationMetadata.create(total_items=total_items, page=page, limit=limit)
    return SubmissionListResponse(items=items, pagination=pagination)


@router.get(
    "/{submission_id}",
    response_model=SubmissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Administrative get submission by ID",
    description="Retrieve any submission by ID regardless of status for administrators.",
)
def get_admin_submission(
    submission_id: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    submission = SubmissionService.get_submission_by_id(
        db=db,
        submission_id=submission_id,
        is_admin=True,
    )
    return submission

