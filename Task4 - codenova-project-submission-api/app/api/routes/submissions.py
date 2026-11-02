from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.dependencies import get_optional_admin
from app.models.admin import Admin
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionResponse,
    SubmissionListResponse,
    PaginationMetadata,
)
from app.services.submission_service import SubmissionService
from app.core.exceptions import UnauthorizedException

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.post(
    "",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a project",
    description="Submit a new project for review. Submissions always start in 'Pending' status.",
)
def create_submission(
    submission_in: SubmissionCreate,
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    submission = SubmissionService.create_submission(db, submission_in)
    return submission


@router.get(
    "",
    response_model=SubmissionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List, search, filter, and paginate submissions",
    description="Retrieve submissions. Public users only receive 'Approved' projects.",
)
def list_submissions(
    q: Optional[str] = Query(None, description="Search keyword in title or description"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    status: Optional[str] = Query(None, description="Filter by status (authorized administrators only)"),
    page: int = Query(1, ge=1, description="Page number, 1-indexed"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Field to sort by (created_at, title, domain, status, updated_at)"),
    sort_order: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
    admin: Optional[Admin] = Depends(get_optional_admin),
    db: Session = Depends(get_db),
) -> SubmissionListResponse:
    is_admin = admin is not None
    if status is not None and not is_admin:
        raise UnauthorizedException("Status filtering requires administrator authentication")

    items, total_items = SubmissionService.list_submissions(
        db=db,
        is_admin=is_admin,
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
    summary="Retrieve a project submission by ID",
    description="Retrieve project details. Public users can only see Approved projects; non-approved items return 404.",
)
def get_submission(
    submission_id: str,
    admin: Optional[Admin] = Depends(get_optional_admin),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    is_admin = admin is not None
    submission = SubmissionService.get_submission_by_id(db, submission_id, is_admin=is_admin)
    return submission

