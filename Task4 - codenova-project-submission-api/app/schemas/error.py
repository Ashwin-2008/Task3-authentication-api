from typing import Any, List
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: List[Any] = []


class ErrorResponse(BaseModel):
    error: ErrorDetail

