from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import asyncio
import time
import psutil
import os
import random
import logging
import requests
from typing import Dict, Any
from ..models import HealthResponse, MetricsResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

start_time = time.time()
request_count = 0
health_check_failures = 0

# Health status simulation
health_status = {
    "database": "healthy",
    "cache": "healthy", 
    "external_service": "healthy",
    "disk_space": "healthy",
    "memory": "healthy"
}

# Error simulation settings
health_simulation = {
    "intermittent_failures": False,
    "memory_pressure": False,
    "disk_pressure": False,
    "slow_responses": False,
    "cascade_failures": False
}

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(request: Request):
    """Enhanced health check with comprehensive error simulation"""
    global health_check_failures, request_count
    request_count += 1
    
    # Simulate slow responses
    if health_simulation.get("slow_responses") and random.random() < 0.3:
        delay = random.uniform(2.0, 5.0)
        logger.warning(f"Simulating slow health check: {delay:.2f}s delay")
        await asyncio.sleep(delay)
    
    # Simulate intermittent failures
    if health_simulation.get("intermittent_failures") and random.random() < 0.15:
        health_check_failures += 1
        logger.error(f"Health check failure #{health_check_failures}")
        
        failure_reasons = [
            "Database connection timeout",
            "Cache service unavailable", 
            "External dependency unreachable",
            "Memory threshold exceeded",
            "Disk space critically low"
        ]
        
        reason = random.choice(failure_reasons)
        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {reason}",
            headers={"Retry-After": "30"}
        )
    
    # Check system resources and simulate pressure scenarios
    try:
        system_health = await check_system_health()
        
        if not system_health["healthy"]:
            logger.error(f"System health degraded: {system_health['issues']}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "degraded",
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "1.0.0",
                    "issues": system_health["issues"],
                    "checks": system_health["checks"]
                }
            )
        
        # Random chance of reporting degraded status even when healthy
        if random.random() < 0.05:  # 5% chance
            logger.warning("Reporting degraded status for testing")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "degraded", 
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "1.0.0",
                    "message": "System experiencing intermittent issues"
                }
            )
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0"
        )
        
    except Exception as e:
        health_check_failures += 1
        logger.error(f"Health check exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed with error: {str(e)}"
        )

async def check_system_health():
    """Check various system components for health"""
    issues = []
    checks = {}
    
    try:
        # Memory check with simulation
        memory = psutil.virtual_memory()
        memory_threshold = 85.0  # Normal threshold
        
        if health_simulation.get("memory_pressure"):
            memory_threshold = 50.0  # Simulate pressure at lower usage
        
        if memory.percent > memory_threshold:
            issues.append(f"High memory usage: {memory.percent:.1f}%")
        
        checks["memory"] = {
            "status": "healthy" if memory.percent <= memory_threshold else "degraded",
            "usage_percent": memory.percent,
            "threshold": memory_threshold
        }
        
        # Disk check with simulation  
        disk = psutil.disk_usage('/')
        disk_threshold = 90.0  # Normal threshold
        
        if health_simulation.get("disk_pressure"):
            disk_threshold = 60.0  # Simulate pressure at lower usage
            
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > disk_threshold:
            issues.append(f"High disk usage: {disk_percent:.1f}%")
            
        checks["disk"] = {
            "status": "healthy" if disk_percent <= disk_threshold else "degraded", 
            "usage_percent": disk_percent,
            "threshold": disk_threshold
        }
        
        # CPU check
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80.0:
            issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            
        checks["cpu"] = {
            "status": "healthy" if cpu_percent <= 80.0 else "degraded",
            "usage_percent": cpu_percent,
            "threshold": 80.0
        }
        
        # Simulate external dependency checks
        if health_simulation.get("cascade_failures") and random.random() < 0.2:
            issues.append("External service dependency failed")
            checks["external_service"] = {
                "status": "failed",
                "error": "Connection timeout to external API"
            }
        else:
            checks["external_service"] = {"status": "healthy"}
        
        # Database simulation
        if random.random() < 0.05:  # 5% chance of DB issues
            issues.append("Database connection pool exhausted")
            checks["database"] = {
                "status": "degraded",
                "active_connections": 95,
                "max_connections": 100
            }
        else:
            checks["database"] = {"status": "healthy"}
            
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "checks": checks
        }
        
    except Exception as e:
        logger.error(f"System health check failed: {str(e)}")
        return {
            "healthy": False,
            "issues": [f"Health check system error: {str(e)}"],
            "checks": {"system": {"status": "error", "error": str(e)}}
        }

@router.get("/health/deep", tags=["Health"])
async def deep_health_check():
    """Comprehensive health check with detailed component status"""
    
    # Simulate various failure scenarios
    if random.random() < 0.1:  # 10% chance
        logger.error("Deep health check failed")
        raise HTTPException(
            status_code=503,
            detail="Deep health check revealed critical issues"
        )
    
    try:
        # Simulate checking multiple services
        services = {
            "database": await simulate_database_check(),
            "cache": await simulate_cache_check(), 
            "message_queue": await simulate_message_queue_check(),
            "external_apis": await simulate_external_api_check(),
            "file_system": await simulate_filesystem_check()
        }
        
        # Determine overall health
        failed_services = [name for name, status in services.items() 
                          if status["status"] != "healthy"]
        
        overall_status = "healthy" if not failed_services else "degraded"
        status_code = 200 if overall_status == "healthy" else 503
        
        response_data = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "services": services,
            "failed_services": failed_services,
            "total_checks": len(services),
            "passed_checks": len(services) - len(failed_services)
        }
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
        
    except Exception as e:
        logger.error(f"Deep health check exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Deep health check failed: {str(e)}"
        )

async def simulate_database_check():
    """Simulate database health check"""
    if health_simulation.get("cascade_failures") and random.random() < 0.15:
        return {
            "status": "failed",
            "error": "Connection timeout after 5000ms",
            "last_successful_connection": "2024-01-15T10:30:00Z"
        }
    elif random.random() < 0.1:
        return {
            "status": "degraded", 
            "warning": "High connection pool usage",
            "active_connections": 85,
            "max_connections": 100,
            "response_time_ms": 450
        }
    
    return {
        "status": "healthy",
        "response_time_ms": random.randint(10, 50),
        "active_connections": random.randint(5, 20),
        "max_connections": 100
    }

async def simulate_cache_check():
    """Simulate cache service health check"""
    if random.random() < 0.08:
        return {
            "status": "failed",
            "error": "Redis connection refused",
            "memory_usage": "unknown"
        }
    
    return {
        "status": "healthy",
        "memory_usage": f"{random.randint(200, 800)}MB",
        "hit_ratio": f"{random.randint(85, 98)}%",
        "response_time_ms": random.randint(1, 5)
    }

async def simulate_message_queue_check():
    """Simulate message queue health check"""
    if random.random() < 0.05:
        return {
            "status": "degraded",
            "warning": "High queue depth",
            "queue_depth": 15000,
            "processing_rate": "150 msg/sec"
        }
    
    return {
        "status": "healthy", 
        "queue_depth": random.randint(0, 100),
        "processing_rate": f"{random.randint(200, 500)} msg/sec"
    }

async def simulate_external_api_check():
    """Simulate external API dependency check"""
    if random.random() < 0.12:
        return {
            "status": "failed",
            "error": "HTTP 503 Service Unavailable",
            "endpoint": "https://api.external-service.com/health",
            "last_success": "2024-01-15T09:45:00Z"
        }
    
    return {
        "status": "healthy",
        "response_time_ms": random.randint(100, 300),
        "endpoint": "https://api.external-service.com/health"
    }

async def simulate_filesystem_check():
    """Simulate filesystem health check"""
    if health_simulation.get("disk_pressure") and random.random() < 0.2:
        return {
            "status": "degraded", 
            "warning": "Low disk space",
            "available_gb": 2.1,
            "total_gb": 100.0,
            "usage_percent": 97.9
        }
    
    disk = psutil.disk_usage('/')
    return {
        "status": "healthy",
        "available_gb": round(disk.free / (1024**3), 1),
        "total_gb": round(disk.total / (1024**3), 1), 
        "usage_percent": round((disk.used / disk.total) * 100, 1)
    }

@router.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def get_metrics():
    """Enhanced metrics with error simulation"""
    global request_count
    request_count += 1
    
    # Simulate metrics collection failures
    if random.random() < 0.05:  # 5% chance
        logger.error("Metrics collection failed")
        raise HTTPException(
            status_code=503,
            detail="Unable to collect metrics at this time"
        )
    
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Simulate corrupted metrics occasionally
        if random.random() < 0.03:
            logger.warning("Returning potentially corrupted metrics")
            return MetricsResponse(
                total_requests=-1,  # Invalid value
                active_connections=process.connections().__len__(),
                uptime_seconds=time.time() - start_time,
                memory_usage_mb=memory_info.rss / (1024 * 1024)
            )
        
        return MetricsResponse(
            total_requests=request_count,
            active_connections=len(process.connections()),
            uptime_seconds=time.time() - start_time,
            memory_usage_mb=memory_info.rss / (1024 * 1024)
        )
        
    except psutil.Error as e:
        logger.error(f"PSUtil error in metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"System metrics collection failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve system metrics"
        )

@router.get("/readiness", tags=["Health"])
async def readiness_check():
    """Readiness check that can fail independently from health"""
    
    # Simulate readiness failures (different from health)
    if random.random() < 0.08:  # 8% chance
        logger.warning("Service not ready")
        raise HTTPException(
            status_code=503,
            detail="Service not ready to accept traffic"
        )
    
    # Check if service dependencies are ready
    dependencies_ready = {
        "database_migration": random.choice([True, True, True, False]),
        "config_loaded": True,
        "cache_warmed": random.choice([True, True, False]),
    }
    
    if not all(dependencies_ready.values()):
        failed_deps = [dep for dep, ready in dependencies_ready.items() if not ready]
        logger.warning(f"Dependencies not ready: {failed_deps}")
        
        return JSONResponse(
            status_code=503,
            content={
                "ready": False,
                "timestamp": datetime.utcnow().isoformat(),
                "dependencies": dependencies_ready,
                "failed_dependencies": failed_deps
            }
        )
    
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": dependencies_ready
    }

@router.get("/liveness", tags=["Health"])
async def liveness_check():
    """Liveness check that indicates if application should be restarted"""
    
    # Simulate deadlock or unrecoverable states
    if random.random() < 0.02:  # 2% chance
        logger.critical("Liveness check failed - application may need restart")
        raise HTTPException(
            status_code=503,
            detail="Application is in unrecoverable state"
        )
    
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "pid": os.getpid(),
        "uptime_seconds": time.time() - start_time
    }

# Health simulation control endpoints
@router.post("/health-simulation/enable")
async def enable_health_simulation(simulation_types: dict):
    """Enable health check error simulation"""
    global health_simulation
    
    valid_types = {
        "intermittent_failures", "memory_pressure", "disk_pressure", 
        "slow_responses", "cascade_failures"
    }
    
    for sim_type, enabled in simulation_types.items():
        if sim_type in valid_types:
            health_simulation[sim_type] = enabled
            logger.info(f"Health simulation {sim_type}: {'enabled' if enabled else 'disabled'}")
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown simulation type: {sim_type}"
            )
    
    return {
        "message": "Health simulation settings updated",
        "current_settings": health_simulation
    }

@router.get("/health-simulation/status")
async def get_health_simulation_status():
    """Get current health simulation settings"""
    return {
        "health_simulation_status": health_simulation,
        "available_simulation_types": [
            "intermittent_failures",
            "memory_pressure", 
            "disk_pressure",
            "slow_responses",
            "cascade_failures"
        ],
        "health_check_failures": health_check_failures,
        "total_requests": request_count
    }