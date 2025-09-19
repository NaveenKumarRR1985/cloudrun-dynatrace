from fastapi import APIRouter
from datetime import datetime
import time
import psutil
import os
from ..models import HealthResponse, MetricsResponse

router = APIRouter()

start_time = time.time()
request_count = 0

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow()
    )

@router.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def get_metrics():
    """Basic application metrics."""
    global request_count
    request_count += 1
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return MetricsResponse(
        total_requests=request_count,
        active_connections=len(process.connections()),
        uptime_seconds=time.time() - start_time,
        memory_usage_mb=memory_info.rss / (1024 * 1024)
    )
