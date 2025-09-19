from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import random
import asyncio
from ..models import UserRequest, UserResponse

router = APIRouter()

# Simple in-memory storage
users_db = []

@router.get("/")
async def root():
    return {
        "message": "FastAPI OpenTelemetry Demo",
        "version": "1.0.0",
        "docs": "/docs"
    }

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserRequest):
    new_user = UserResponse(
        id=len(users_db) + 1,
        name=user.name,
        email=user.email,
        age=user.age,
        created_at=datetime.utcnow()
    )
    users_db.append(new_user)
    return new_user

@router.get("/users", response_model=List[UserResponse])
async def get_users():
    return users_db

@router.get("/simulate-work")
async def simulate_work():
    delay = random.uniform(0.1, 0.5)
    await asyncio.sleep(delay)
    return {
        "message": "Work completed",
        "processing_time": f"{delay:.2f} seconds",
        "timestamp": datetime.utcnow()
    }
