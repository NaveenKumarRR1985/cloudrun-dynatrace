from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"

class UserRequest(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    created_at: datetime

class MetricsResponse(BaseModel):
    total_requests: int
    active_connections: int
    uptime_seconds: float
    memory_usage_mb: float
