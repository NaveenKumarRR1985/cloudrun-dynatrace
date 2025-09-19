from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .routers import health, api, web
import os
import time
import logging
import traceback
from datetime import datetime

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="FastAPI OpenTelemetry Demo with Error Simulation",
    description="A comprehensive FastAPI application with OpenTelemetry auto-instrumentation and error simulation capabilities for Dynatrace testing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
except Exception as e:
    logger.error(f"Failed to mount static files: {str(e)}")

# Global error tracking
error_tracker = {
    "total_errors": 0,
    "error_types": {},
    "last_error": None,
    "error_rate": 0.0
}

# Request tracking middleware with error handling
@app.middleware("http")
async def comprehensive_request_middleware(request: Request, call_next):
    """Enhanced middleware with error tracking and request monitoring"""
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Update request counter
        from .routers import health
        health.request_count += 1
        
        # Calculate response time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # Track errors
        error_tracker["total_errors"] += 1
        error_tracker["last_error"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "path": str(request.url),
            "method": request.method
        }
        
        error_type = type(e).__name__
        error_tracker["error_types"][error_type] = error_tracker["error_types"].get(error_type, 0) + 1
        
        # Re-raise the exception to be handled by exception handlers
        raise e

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Comprehensive Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with detailed logging"""
    error_tracker["total_errors"] += 1
    error_type = f"HTTP_{exc.status_code}"
    error_tracker["error_types"][error_type] = error_tracker["error_types"].get(error_type, 0) + 1
    
    # Log the HTTP exception
    logger.error(f"HTTP Exception {exc.status_code}: {exc.detail} - Path: {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code}",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "method": request.method,
            "request_id": id(request)
        },
        headers=getattr(exc, 'headers', None)
    )

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle Starlette HTTP exceptions"""
    error_tracker["total_errors"] += 1
    error_type = f"STARLETTE_HTTP_{exc.status_code}"
    error_tracker["error_types"][error_type] = error_tracker["error_types"].get(error_type, 0) + 1
    
    logger.error(f"Starlette HTTP Exception {exc.status_code}: {exc.detail} - Path: {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code}",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "type": "starlette_http_exception"
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    error_tracker["total_errors"] += 1
    error_tracker["error_types"]["VALIDATION_ERROR"] = error_tracker["error_types"].get("VALIDATION_ERROR", 0) + 1
    
    logger.error(f"Validation Error: {str(exc)} - Path: {request.url}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": "Request validation failed",
            "errors": exc.errors(),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "body": str(exc.body) if hasattr(exc, 'body') else None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    error_tracker["total_errors"] += 1
    error_type = type(exc).__name__
    error_tracker["error_types"][error_type] = error_tracker["error_types"].get(error_type, 0) + 1
    
    # Log the full exception with traceback
    logger.critical(f"Unhandled Exception: {str(exc)} - Path: {request.url}")
    logger.critical(f"Exception type: {type(exc).__name__}")
    logger.critical(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "exception_type": type(exc).__name__,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "method": request.method,
            "error_id": f"ERR_{int(time.time())}"
        }
    )

# Include routers with error handling
try:
    app.include_router(health.router, prefix="/api", tags=["Health"])
    logger.info("Health router included successfully")
except Exception as e:
    logger.error(f"Failed to include health router: {str(e)}")

try:
    app.include_router(api.router, prefix="/api", tags=["API"])
    logger.info("API router included successfully")
except Exception as e:
    logger.error(f"Failed to include API router: {str(e)}")

try:
    app.include_router(web.router, tags=["Web UI"])
    logger.info("Web router included successfully")
except Exception as e:
    logger.error(f"Failed to include web router: {str(e)}")

# Additional error tracking endpoints
@app.get("/api/error-tracking")
async def get_error_tracking():
    """Get comprehensive error tracking information"""
    # Try to get request count from health router, fallback to 0
    try:
        from .routers import health
        total_requests = getattr(health, 'request_count', 0)
    except:
        total_requests = 1  # Avoid division by zero
    
    error_rate = (error_tracker["total_errors"] / max(total_requests, 1)) * 100
    
    return {
        "total_errors": error_tracker["total_errors"],
        "total_requests": total_requests,
        "error_rate_percent": round(error_rate, 2),
        "error_types": error_tracker["error_types"],
        "last_error": error_tracker["last_error"],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/clear-error-tracking")
async def clear_error_tracking():
    """Clear error tracking statistics"""
    global error_tracker
    error_tracker = {
        "total_errors": 0,
        "error_types": {},
        "last_error": None,
        "error_rate": 0.0
    }
    
    logger.info("Error tracking statistics cleared")
    return {
        "message": "Error tracking statistics cleared",
        "timestamp": datetime.utcnow().isoformat()
    }

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup with comprehensive initialization"""
    try:
        logger.info("🚀 FastAPI application starting up!")
        logger.info(f"📊 OTEL endpoint: {os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'Not configured')}")
        logger.info(f"🎨 Beautiful UI available at http://localhost:8000")
        logger.info(f"📋 API Documentation at http://localhost:8000/api/docs")
        logger.info(f"🔧 Error simulation endpoints enabled")
        logger.info(f"📈 Dynatrace monitoring capabilities active")
        
        # Initialize error tracking
        error_tracker["startup_time"] = datetime.utcnow().isoformat()
        
        # Log environment information
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"Debug mode: {os.getenv('DEBUG', 'False')}")
        
    except Exception as e:
        logger.critical(f"Startup failed: {str(e)}")
        logger.critical(f"Startup traceback: {traceback.format_exc()}")
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown with cleanup"""
    try:
        logger.info("🛑 FastAPI application shutting down...")
        logger.info(f"Total errors during runtime: {error_tracker['total_errors']}")
        logger.info(f"Error types: {error_tracker['error_types']}")
        logger.info("Application shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# Health check for the entire application
@app.get("/ping")
async def ping():
    """Simple ping endpoint for basic connectivity testing"""
    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "ok"
    }

# Root endpoint with error simulation
@app.get("/")
async def root():
    """Root endpoint that redirects to dashboard"""
    # Random chance of root endpoint failure for testing
    import random
    if random.random() < 0.01:  # 1% chance
        logger.error("Root endpoint random failure for testing")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable at root"
        )
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=302)

if __name__ == "__main__":
    import uvicorn
    
    try:
        logger.info("Starting server with uvicorn...")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}")
        raise e