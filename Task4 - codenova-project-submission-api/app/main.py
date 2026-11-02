from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.exceptions import AppException
from app.db.init_db import init_db
from app.api.routes import auth, submissions, moderation


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler to initialize database schema on startup."""
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "RESTful Project Submission API for CodeNova Backend Internship Task 4. "
        "Allows public project submissions, strict URL validation, search, domain filtering, "
        "and administrative moderation with signed JWT authentication."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions with standardized error payload."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic/FastAPI validation errors with standardized format."""
    formatted_errors = []
    for err in exc.errors():
        loc = err.get("loc", ())
        # Filter out body prefix if present for cleaner field references
        field_parts = [str(x) for x in loc if x != "body"]
        field_name = ".".join(field_parts) if field_parts else "request"
        formatted_errors.append({
            "field": field_name,
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "validation_error"),
        })

    return JSONResponse(
        status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The submitted data is invalid.",
                "details": formatted_errors,
            }
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions."""
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_SERVER_ERROR",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": str(exc.detail),
                "details": [],
            }
        },
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler preventing tracebacks from leaking to API clients."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred.",
                "details": [],
            }
        },
    )


# Health check endpoint
@app.get(
    f"{settings.API_V1_PREFIX}/health",
    tags=["System"],
    summary="Health check endpoint",
    description="Check system health and status.",
    status_code=status.HTTP_200_OK,
)
def health_check() -> dict:
    return {"status": "ok"}


# Root informational endpoint
@app.get(
    "/",
    tags=["System"],
    summary="Root API info",
    include_in_schema=False,
)
def root() -> dict:
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }


# Register API v1 routes
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(submissions.router, prefix=settings.API_V1_PREFIX)
app.include_router(moderation.router, prefix=settings.API_V1_PREFIX)
