from pydantic import BaseModel
from typing import Optional


class TruthEntry(BaseModel):
    id: str
    truth: str


class ErrorResponse(BaseModel):
    detail: str
    status_code: int
    timestamp: str


class HealthCheckResponse(BaseModel):
    status: str
    uptime: Optional[str] = None
    version: str
