import math
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.validators.urls import validate_github_url, validate_demo_url


class SubmissionCreate(BaseModel):
    """Schema for public project submissions."""

    title: str = Field(..., min_length=3, max_length=150, description="Project title")
    description: str = Field(..., min_length=10, max_length=3000, description="Detailed project description")
    domain: str = Field(..., min_length=2, max_length=100, description="Project domain/category")
    github_url: str = Field(..., description="Valid GitHub repository HTTPS URL")
    demo_url: str = Field(..., description="Valid live demo HTTPS URL")

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "description", "domain", mode="before")
    @classmethod
    def strip_whitespace_and_validate_non_empty(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Field cannot be empty or whitespace only")
        return v

    @field_validator("github_url")
    @classmethod
    def validate_github(cls, v: str) -> str:
        return validate_github_url(v)

    @field_validator("demo_url")
    @classmethod
    def validate_demo(cls, v: str) -> str:
        return validate_demo_url(v)


class SubmissionResponse(BaseModel):
    """Schema for returning submission details."""

    id: str
    title: str
    description: str
    domain: str
    github_url: str
    demo_url: str
    status: str
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaginationMetadata(BaseModel):
    """Metadata describing a paginated response collection."""

    total_items: int = Field(..., ge=0, description="Total number of matching items")
    total_pages: int = Field(..., ge=0, description="Total number of pages (0 if no items)")
    current_page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    has_next: bool = Field(..., description="Whether a next page exists")
    has_previous: bool = Field(..., description="Whether a previous page exists")

    @classmethod
    def create(cls, total_items: int, page: int, limit: int) -> "PaginationMetadata":
        if total_items == 0:
            total_pages = 0
            has_next = False
            has_previous = False
        else:
            total_pages = math.ceil(total_items / limit)
            has_next = page < total_pages
            has_previous = page > 1

        return cls(
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
            page_size=limit,
            has_next=has_next,
            has_previous=has_previous,
        )


class SubmissionListResponse(BaseModel):
    """Standardized list response with pagination metadata."""

    items: List[SubmissionResponse]
    pagination: PaginationMetadata

