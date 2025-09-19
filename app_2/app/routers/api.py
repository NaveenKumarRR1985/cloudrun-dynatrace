from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import random
import asyncio
import time
import logging
from ..models import UserRequest, UserResponse

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory storage
users_db = []

# Custom exceptions for application errors
class DatabaseConnectionError(Exception):
    """Simulates database connection issues"""
    pass

class ValidationError(Exception):
    """Simulates data validation errors"""
    pass

class ExternalServiceError(Exception):
    """Simulates external service failures"""
    pass

class RateLimitError(Exception):
    """Simulates rate limiting errors"""
    pass

# Error simulation flags
error_simulation = {
    "database_errors": False,
    "validation_errors": False,
    "service_errors": False,
    "rate_limit_errors": False,
    "random_errors": False
}

@router.get("/")
async def root():
    """Root endpoint with potential errors"""
    if error_simulation.get("random_errors") and random.random() < 0.1:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    
    return {
        "message": "FastAPI OpenTelemetry Demo",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational",
        "timestamp": datetime.utcnow()
    }

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserRequest, request: Request):
    """Create user with comprehensive error handling"""
    
    # Simulate rate limiting
    if error_simulation.get("rate_limit_errors") and random.random() < 0.2:
        logger.warning(f"Rate limit exceeded for IP: {request.client.host}")
        raise HTTPException(
            status_code=429, 
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": "60"}
        )
    
    # Simulate validation errors
    if error_simulation.get("validation_errors") and random.random() < 0.15:
        logger.error(f"Validation failed for user: {user.name}")
        raise HTTPException(
            status_code=422,
            detail="Validation failed: Invalid user data provided"
        )
    
    # Simulate database connection errors
    if error_simulation.get("database_errors") and random.random() < 0.1:
        logger.error("Database connection failed during user creation")
        raise DatabaseConnectionError("Unable to connect to user database")
    
    # Email validation
    if not user.email or "@" not in user.email:
        raise HTTPException(
            status_code=400,
            detail="Invalid email format provided"
        )
    
    # Check for duplicate email
    if any(existing_user.email == user.email for existing_user in users_db):
        raise HTTPException(
            status_code=409,
            detail=f"User with email {user.email} already exists"
        )
    
    # Age validation
    if user.age is not None and (user.age < 0 or user.age > 150):
        raise HTTPException(
            status_code=400,
            detail="Age must be between 0 and 150"
        )
    
    try:
        # Simulate processing delay
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        new_user = UserResponse(
            id=len(users_db) + 1,
            name=user.name,
            email=user.email,
            age=user.age,
            created_at=datetime.utcnow()
        )
        
        users_db.append(new_user)
        logger.info(f"User created successfully: {new_user.id}")
        
        return new_user
        
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while creating user"
        )

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    search: Optional[str] = None
):
    """Get users with filtering and error simulation"""
    
    # Simulate service errors
    if error_simulation.get("service_errors") and random.random() < 0.05:
        logger.error("External service dependency failed")
        raise HTTPException(
            status_code=502,
            detail="External service unavailable"
        )
    
    # Validate parameters
    if offset and offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset cannot be negative"
        )
    
    if limit and limit <= 0:
        raise HTTPException(
            status_code=400,
            detail="Limit must be greater than 0"
        )
    
    try:
        filtered_users = users_db
        
        # Apply search filter
        if search:
            filtered_users = [
                user for user in users_db 
                if search.lower() in user.name.lower() or search.lower() in user.email.lower()
            ]
        
        # Apply pagination
        if offset:
            filtered_users = filtered_users[offset:]
        
        if limit:
            filtered_users = filtered_users[:limit]
        
        return filtered_users
        
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve users"
        )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get specific user with error handling"""
    
    if user_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="User ID must be a positive integer"
        )
    
    # Simulate random errors
    if error_simulation.get("random_errors") and random.random() < 0.08:
        raise HTTPException(
            status_code=500,
            detail="Random internal server error"
        )
    
    user = next((user for user in users_db if user.id == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )
    
    return user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete user with error handling"""
    
    if user_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="User ID must be a positive integer"
        )
    
    # Simulate database errors
    if error_simulation.get("database_errors") and random.random() < 0.1:
        logger.error(f"Database error during user deletion: {user_id}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred during deletion"
        )
    
    user_index = next(
        (i for i, user in enumerate(users_db) if user.id == user_id), 
        None
    )
    
    if user_index is None:
        raise HTTPException(
            status_code=404,
            detail=f"User with ID {user_id} not found"
        )
    
    try:
        deleted_user = users_db.pop(user_index)
        logger.info(f"User deleted: {deleted_user.id}")
        
        return {
            "message": f"User {user_id} deleted successfully",
            "deleted_user": deleted_user
        }
        
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete user"
        )

@router.get("/simulate-work")
async def simulate_work():
    """Work simulation with potential errors"""
    
    # Random chance of various errors
    error_chance = random.random()
    
    if error_chance < 0.05:  # 5% chance
        logger.error("Simulated timeout error")
        raise HTTPException(
            status_code=408,
            detail="Request timeout during work simulation"
        )
    elif error_chance < 0.08:  # 3% chance
        logger.error("Simulated service unavailable")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable"
        )
    elif error_chance < 0.10:  # 2% chance
        logger.error("Simulated internal server error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during work processing"
        )
    
    try:
        delay = random.uniform(0.1, 0.5)
        await asyncio.sleep(delay)
        
        return {
            "message": "Work completed successfully",
            "processing_time": f"{delay:.2f} seconds",
            "timestamp": datetime.utcnow(),
            "worker_id": random.randint(1, 100)
        }
        
    except asyncio.TimeoutError:
        logger.error("Work simulation timed out")
        raise HTTPException(
            status_code=408,
            detail="Work simulation timed out"
        )
    except Exception as e:
        logger.error(f"Unexpected error in work simulation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred during work simulation"
        )

# Error simulation control endpoints
@router.post("/error-simulation/enable")
async def enable_error_simulation(error_types: dict):
    """Enable specific error types for testing"""
    global error_simulation
    
    valid_types = {
        "database_errors", "validation_errors", 
        "service_errors", "rate_limit_errors", "random_errors"
    }
    
    for error_type, enabled in error_types.items():
        if error_type in valid_types:
            error_simulation[error_type] = enabled
            logger.info(f"Error simulation {error_type}: {'enabled' if enabled else 'disabled'}")
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown error type: {error_type}"
            )
    
    return {
        "message": "Error simulation settings updated",
        "current_settings": error_simulation
    }

@router.get("/error-simulation/status")
async def get_error_simulation_status():
    """Get current error simulation settings"""
    return {
        "error_simulation_status": error_simulation,
        "available_error_types": [
            "database_errors",
            "validation_errors", 
            "service_errors",
            "rate_limit_errors",
            "random_errors"
        ]
    }

@router.post("/trigger-error/{error_code}")
async def trigger_specific_error(error_code: int, message: Optional[str] = None):
    """Manually trigger specific HTTP error codes"""
    
    error_messages = {
        400: "Bad Request - Invalid input provided",
        401: "Unauthorized - Authentication required",
        403: "Forbidden - Access denied",
        404: "Not Found - Resource does not exist", 
        409: "Conflict - Resource already exists",
        422: "Unprocessable Entity - Validation failed",
        429: "Too Many Requests - Rate limit exceeded",
        500: "Internal Server Error - Server encountered an error",
        502: "Bad Gateway - Upstream server error",
        503: "Service Unavailable - Service temporarily down",
        504: "Gateway Timeout - Upstream server timeout"
    }
    
    if error_code not in error_messages:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported error code: {error_code}"
        )
    
    error_detail = message or error_messages[error_code]
    logger.error(f"Manually triggered error {error_code}: {error_detail}")
    
    # Add retry-after header for 429 and 503
    headers = {}
    if error_code in [429, 503]:
        headers["Retry-After"] = "60"
    
    raise HTTPException(
        status_code=error_code,
        detail=error_detail,
        headers=headers if headers else None
    )

# # Custom exception handlers
# @router.exception_handler(DatabaseConnectionError)
# async def database_error_handler(request: Request, exc: DatabaseConnectionError):
#     logger.error(f"Database connection error: {str(exc)}")
#     return JSONResponse(
#         status_code=503,
#         content={
#             "error": "Database Connection Error",
#             "detail": str(exc),
#             "timestamp": datetime.utcnow().isoformat(),
#             "path": str(request.url)
#         }
#     )

# @router.exception_handler(ValidationError)
# async def validation_error_handler(request: Request, exc: ValidationError):
#     logger.error(f"Validation error: {str(exc)}")
#     return JSONResponse(
#         status_code=422,
#         content={
#             "error": "Validation Error", 
#             "detail": str(exc),
#             "timestamp": datetime.utcnow().isoformat(),
#             "path": str(request.url)
#         }
#     )

# @router.exception_handler(ExternalServiceError)
# async def service_error_handler(request: Request, exc: ExternalServiceError):
#     logger.error(f"External service error: {str(exc)}")
#     return JSONResponse(
#         status_code=502,
#         content={
#             "error": "External Service Error",
#             "detail": str(exc), 
#             "timestamp": datetime.utcnow().isoformat(),
#             "path": str(request.url)
#         }
#     )

# @router.exception_handler(RateLimitError) 
# async def rate_limit_error_handler(request: Request, exc: RateLimitError):
#     logger.warning(f"Rate limit exceeded: {str(exc)}")
#     return JSONResponse(
#         status_code=429,
#         content={
#             "error": "Rate Limit Exceeded",
#             "detail": str(exc),
#             "timestamp": datetime.utcnow().isoformat(), 
#             "path": str(request.url)
#         },
#         headers={"Retry-After": "60"}
#     )