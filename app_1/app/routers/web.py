from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import time
import psutil
import os
from datetime import datetime
import socket
import platform

# Import from other routers to access data
from . import api, health

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/users-ui", response_class=HTMLResponse)
async def users_page(request: Request):
    """Users management page"""
    users = api.users_db
    return templates.TemplateResponse("users.html", {
        "request": request, 
        "users": users
    })

@router.get("/metrics-ui", response_class=HTMLResponse)
async def metrics_page(request: Request):
    """Metrics dashboard page"""
    return templates.TemplateResponse("metrics.html", {"request": request})

@router.post("/users-ui")
async def create_user_ui(
    request: Request,
    name: str = Form(...),
    email: str = Form(...), 
    age: Optional[int] = Form(None)
):
    """Create user from web form"""
    from ..models import UserRequest, UserResponse
    
    user_request = UserRequest(name=name, email=email, age=age)
    
    # Create user (reuse logic from API)
    new_user = UserResponse(
        id=len(api.users_db) + 1,
        name=user_request.name,
        email=user_request.email,
        age=user_request.age,
        created_at=datetime.utcnow()
    )
    api.users_db.append(new_user)
    
    return RedirectResponse(url="/users-ui", status_code=303)

@router.get("/api/dashboard-data")
async def get_dashboard_data():
    """Enhanced API endpoint for comprehensive dashboard data"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    # Get detailed system information
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    virtual_memory = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')
    
    # Get network statistics
    network_stats = psutil.net_io_counters()
    
    # Get process information
    connections = process.connections()
    threads = process.num_threads()
    
    # Boot time and uptime
    boot_time = psutil.boot_time()
    current_time = time.time()
    system_uptime = current_time - boot_time
    app_uptime = current_time - health.start_time
    
    return {
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": cpu_count,
            "cpu_freq_current": cpu_freq.current if cpu_freq else 0,
            "cpu_freq_max": cpu_freq.max if cpu_freq else 0,
            "memory_percent": virtual_memory.percent,
            "memory_total_gb": round(virtual_memory.total / (1024**3), 2),
            "memory_used_gb": round(virtual_memory.used / (1024**3), 2),
            "memory_available_gb": round(virtual_memory.available / (1024**3), 2),
            "disk_percent": round((disk_usage.used / disk_usage.total) * 100, 1),
            "disk_total_gb": round(disk_usage.total / (1024**3), 2),
            "disk_used_gb": round(disk_usage.used / (1024**3), 2),
            "disk_free_gb": round(disk_usage.free / (1024**3), 2),
            "network_bytes_sent": network_stats.bytes_sent,
            "network_bytes_recv": network_stats.bytes_recv,
            "network_packets_sent": network_stats.packets_sent,
            "network_packets_recv": network_stats.packets_recv,
            "uptime_seconds": system_uptime,
            "platform": platform.system(),
            "hostname": socket.gethostname(),
            "python_version": platform.python_version()
        },
        "app": {
            "total_users": len(api.users_db),
            "total_requests": health.request_count,
            "memory_usage_mb": round(memory_info.rss / (1024 * 1024), 2),
            "memory_usage_percent": round((memory_info.rss / virtual_memory.total) * 100, 2),
            "active_connections": len(connections),
            "threads_count": threads,
            "uptime_seconds": app_uptime,
            "process_id": process.pid,
            "cpu_percent": process.cpu_percent(),
            "open_files": len(process.open_files()) if hasattr(process, 'open_files') else 0
        },
        "performance": {
            "load_average": list(os.getloadavg()) if hasattr(os, 'getloadavg') else [0, 0, 0],
            "cpu_times": psutil.cpu_times()._asdict(),
            "memory_stats": {
                "cached": getattr(virtual_memory, 'cached', 0),
                "buffers": getattr(virtual_memory, 'buffers', 0),
                "shared": getattr(virtual_memory, 'shared', 0)
            }
        }
    }

@router.get("/api/system-history")
async def get_system_history():
    """Get historical system performance data for charts"""
    # This would typically come from a database or time-series storage
    # For now, we'll return current data that JavaScript can use to build history
    current_data = await get_dashboard_data()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": current_data["system"]["cpu_percent"],
        "memory": current_data["system"]["memory_percent"],
        "disk": current_data["system"]["disk_percent"],
        "network_sent": current_data["system"]["network_bytes_sent"],
        "network_recv": current_data["system"]["network_bytes_recv"],
        "app_memory": current_data["app"]["memory_usage_mb"],
        "requests": current_data["app"]["total_requests"]
    }
