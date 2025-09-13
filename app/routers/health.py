import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings

router = APIRouter(
    prefix="/api/health",
    tags=["health"]
)

@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check with environment validation"""
    
    # Check required environment variables through settings
    env_checks = {
        "BEAG_API_KEY": bool(settings.beag_api_key),
        "DATABASE_URL": bool(settings.database_url)
    }
    
    # Check database connectivity
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False
    
    # Calculate overall health
    env_healthy = all(env_checks.values())
    overall_health = env_healthy and db_connected
    
    return {
        "status": "healthy" if overall_health else "unhealthy",
        "database": {
            "connected": db_connected
        },
        "environment": {
            "configured": env_healthy,
            "variables": env_checks
        },
        "setup_complete": overall_health
    }

@router.get("/setup-status")
async def get_setup_status(db: Session = Depends(get_db)):
    """Detailed setup status for dashboard progress tracking"""
    
    # Backend environment checks through settings
    backend_env = {
        "BEAG_API_KEY": bool(settings.beag_api_key),
        "DATABASE_URL": bool(settings.database_url)
    }
    
    # Database connectivity
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False
    
    # Calculate progress percentages
    backend_progress = sum(backend_env.values()) / len(backend_env) * 100
    database_progress = 100 if db_connected else 0
    
    return {
        "backend": {
            "configured": all(backend_env.values()),
            "progress": backend_progress,
            "environment_variables": backend_env
        },
        "database": {
            "connected": db_connected,
            "progress": database_progress
        },
        "overall_progress": (backend_progress + database_progress) / 2
    }