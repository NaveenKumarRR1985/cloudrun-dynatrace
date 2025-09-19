from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from typing import Optional
import time
import psutil
import os
import random
import logging
import asyncio
from datetime import datetime
import socket
import platform

# Import from other routers to access data
from . import api, health

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page with error testing capabilities"""
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

@router.get("/errors-ui", response_class=HTMLResponse)
async def errors_page(request: Request):
    """Error testing and simulation page"""
    try:
        # Safely access the error simulation dictionaries with defaults
        api_errors = getattr(api, 'error_simulation', {})
        health_errors = getattr(health, 'health_simulation', {})
        
        return templates.TemplateResponse("errors.html", {
            "request": request,
            "api_errors": api_errors,
            "health_errors": health_errors
        })
    except Exception as e:
        # Fallback if there are issues accessing the simulation dictionaries
        logger.error(f"Error loading errors page: {str(e)}")
        return templates.TemplateResponse("errors.html", {
            "request": request,
            "api_errors": {},
            "health_errors": {}
        })

@router.post("/users-ui")
async def create_user_ui(
    request: Request,
    name: str = Form(...),
    email: str = Form(...), 
    age: Optional[int] = Form(None)
):
    """Create user from web form with error handling"""
    try:
        from ..models import UserRequest, UserResponse
        
        user_request = UserRequest(name=name, email=email, age=age)
        
        # Simulate form processing errors
        if random.random() < 0.05:  # 5% chance
            logger.error("Form processing error")
            raise HTTPException(
                status_code=500,
                detail="Error processing user creation form"
            )
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in user creation UI: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during user creation"
        )

@router.get("/api/dashboard-data")
async def get_dashboard_data():
    """Enhanced API endpoint for comprehensive dashboard data with error simulation"""
    
    # Simulate data collection errors
    if random.random() < 0.03:  # 3% chance
        logger.error("Dashboard data collection failed")
        raise HTTPException(
            status_code=503,
            detail="Unable to collect dashboard data"
        )
    
    try:
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
        
        # Safely access error simulation dictionaries
        api_errors = getattr(api, 'error_simulation', {
            "database_errors": False,
            "validation_errors": False,
            "service_errors": False,
            "rate_limit_errors": False,
            "random_errors": False
        })
        
        health_errors = getattr(health, 'health_simulation', {
            "intermittent_failures": False,
            "memory_pressure": False,
            "disk_pressure": False,
            "slow_responses": False,
            "cascade_failures": False
        })
        
        # Simulate occasional data corruption for testing
        if random.random() < 0.02:  # 2% chance
            logger.warning("Simulating corrupted dashboard data")
            return {
                "system": {
                    "cpu_percent": -1,  # Invalid CPU percentage
                    "memory_percent": 150.0,  # Invalid memory percentage
                    "error": "Data corruption detected"
                },
                "app": {
                    "total_users": -5,  # Invalid user count
                    "error": "Corrupted application metrics"
                }
            }
        
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
                "open_files": len(process.open_files()) if hasattr(process, 'open_files') else 0,
                "health_check_failures": getattr(health, 'health_check_failures', 0)
            },
            "performance": {
                "load_average": list(os.getloadavg()) if hasattr(os, 'getloadavg') else [0, 0, 0],
                "cpu_times": psutil.cpu_times()._asdict(),
                "memory_stats": {
                    "cached": getattr(virtual_memory, 'cached', 0),
                    "buffers": getattr(virtual_memory, 'buffers', 0),
                    "shared": getattr(virtual_memory, 'shared', 0)
                }
            },
            "errors": {
                "api_simulation": api_errors,
                "health_simulation": health_errors
            }
        }
        
    except psutil.Error as e:
        logger.error(f"PSUtil error in dashboard data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"System data collection failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in dashboard data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve dashboard data"
        )

@router.get("/api/system-history")
async def get_system_history():
    """Get historical system performance data for charts with error simulation"""
    
    # Simulate history collection errors
    if random.random() < 0.02:  # 2% chance
        logger.error("System history collection failed")
        raise HTTPException(
            status_code=503,
            detail="Unable to retrieve system history"
        )
    
    try:
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving system history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve system history"
        )

# Error testing and simulation endpoints for the UI
@router.post("/api/test-errors")
async def test_specific_error(request: Request):
    """Test specific error scenarios"""
    try:
        data = await request.json()
        error_type = data.get("error_type")
        
        if error_type == "500":
            logger.error("Triggering 500 error for testing")
            raise HTTPException(status_code=500, detail="Internal Server Error - Test")
        
        elif error_type == "503":
            logger.error("Triggering 503 error for testing")
            raise HTTPException(
                status_code=503, 
                detail="Service Unavailable - Test",
                headers={"Retry-After": "30"}
            )
        
        elif error_type == "timeout":
            logger.warning("Simulating timeout for testing")
            await asyncio.sleep(10)  # Long delay to simulate timeout
            return {"message": "This should timeout"}
        
        elif error_type == "memory_leak":
            logger.warning("Simulating memory leak for testing")
            # Create temporary memory pressure
            temp_data = [random.random() for _ in range(1000000)]
            await asyncio.sleep(5)
            del temp_data
            return {"message": "Memory leak simulation completed"}
        
        elif error_type == "database_error":
            logger.error("Simulating database error")
            raise HTTPException(
                status_code=503,
                detail="Database connection failed - Test"
            )
        
        elif error_type == "validation_error":
            logger.error("Simulating validation error")
            raise HTTPException(
                status_code=422,
                detail="Validation failed - Test data invalid"
            )
        
        elif error_type == "auth_error":
            logger.error("Simulating authentication error")
            raise HTTPException(
                status_code=401,
                detail="Authentication required - Test"
            )
        
        elif error_type == "rate_limit":
            logger.warning("Simulating rate limit error")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded - Test",
                headers={"Retry-After": "60"}
            )
        
        else:
            return {"message": f"Unknown error type: {error_type}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in test_specific_error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to execute error test"
        )

@router.post("/api/chaos-monkey")
async def chaos_monkey():
    """Chaos engineering endpoint - randomly triggers various issues"""
    
    chaos_scenarios = [
        {"type": "cpu_spike", "probability": 0.3},
        {"type": "memory_spike", "probability": 0.2},
        {"type": "slow_response", "probability": 0.3},
        {"type": "error_spike", "probability": 0.15},
        {"type": "connection_drop", "probability": 0.05}
    ]
    
    triggered_scenarios = []
    
    for scenario in chaos_scenarios:
        if random.random() < scenario["probability"]:
            triggered_scenarios.append(scenario["type"])
            
            if scenario["type"] == "cpu_spike":
                # Simulate CPU intensive work
                logger.warning("Chaos monkey: CPU spike")
                start_time = time.time()
                while time.time() - start_time < 2:
                    _ = [random.random() for _ in range(1000)]
            
            elif scenario["type"] == "memory_spike":
                # Simulate memory spike
                logger.warning("Chaos monkey: Memory spike")
                temp_data = [random.random() for _ in range(500000)]
                await asyncio.sleep(3)
                del temp_data
            
            elif scenario["type"] == "slow_response":
                # Simulate slow response
                logger.warning("Chaos monkey: Slow response")
                await asyncio.sleep(random.uniform(2, 5))
            
            elif scenario["type"] == "error_spike":
                # Enable random errors temporarily
                logger.warning("Chaos monkey: Error spike")
                api.error_simulation["random_errors"] = True
                await asyncio.sleep(10)
                api.error_simulation["random_errors"] = False
            
            elif scenario["type"] == "connection_drop":
                # Simulate connection issues
                logger.error("Chaos monkey: Connection drop")
                raise HTTPException(
                    status_code=503,
                    detail="Chaos monkey triggered connection drop"
                )
    
    return {
        "message": "Chaos monkey executed",
        "triggered_scenarios": triggered_scenarios,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/api/load-test")
async def simulate_load():
    """Simulate high load on the application"""
    logger.info("Starting load simulation")
    
    try:
        # Simulate multiple concurrent operations
        tasks = []
        
        # Create CPU load
        for _ in range(5):
            tasks.append(asyncio.create_task(cpu_intensive_task()))
        
        # Create memory allocations
        for _ in range(3):
            tasks.append(asyncio.create_task(memory_intensive_task()))
        
        # Simulate database operations
        for _ in range(10):
            tasks.append(asyncio.create_task(simulate_db_operation()))
        
        await asyncio.gather(*tasks)
        
        return {
            "message": "Load test completed",
            "operations": len(tasks),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Load test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Load test execution failed: {str(e)}"
        )

async def cpu_intensive_task():
    """CPU intensive task for load testing"""
    start_time = time.time()
    while time.time() - start_time < 3:
        _ = sum(random.random() for _ in range(10000))
    await asyncio.sleep(0.1)

async def memory_intensive_task():
    """Memory intensive task for load testing"""
    data = []
    for _ in range(100000):
        data.append(random.random())
    await asyncio.sleep(2)
    del data

async def simulate_db_operation():
    """Simulate database operation with potential failures"""
    if random.random() < 0.1:  # 10% chance of failure
        raise Exception("Simulated database operation failed")
    
    # Simulate variable response times
    await asyncio.sleep(random.uniform(0.1, 0.5))
    return {"status": "completed"}

@router.get("/api/error-stats")
async def get_error_statistics():
    """Get error statistics and simulation status"""
    return {
        "health_check_failures": health.health_check_failures,
        "total_requests": health.request_count,
        "simulation_status": {
            "api_errors": api.error_simulation,
            "health_errors": health.health_simulation
        },
        "system_status": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": round((psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100, 1)
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/api/reset-errors")
async def reset_error_counters():
    """Reset error counters and disable simulations"""
    global health
    
    # Reset counters
    health.health_check_failures = 0
    
    # Disable all error simulations
    for key in api.error_simulation:
        api.error_simulation[key] = False
    
    for key in health.health_simulation:
        health.health_simulation[key] = False
    
    logger.info("Error counters reset and simulations disabled")
    
    return {
        "message": "Error statistics reset and simulations disabled",
        "timestamp": datetime.utcnow().isoformat()
    }