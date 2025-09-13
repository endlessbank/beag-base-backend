from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import users, subscriptions, health
from app.services.sync_service import SubscriptionSyncService
import logging
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Beag Boilerplate Backend",
    description="Backend API for Beag.io SaaS boilerplate",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(health.router)


@app.get("/")
async def root():
    return {
        "message": "Beag Boilerplate Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "worker_running": not should_stop_worker
    }


@app.post("/sync-now")
async def manual_sync():
    """Trigger an immediate subscription sync"""
    try:
        result = await sync_subscriptions()
        return {
            "status": "success",
            "message": "Subscription sync completed",
            "result": result
        }
    except Exception as e:
        logger.error(f"Manual sync error: {str(e)}")
        return {
            "status": "error",
            "message": f"Sync failed: {str(e)}"
        }


# Background worker variables
background_task = None
should_stop_worker = False


async def sync_subscriptions():
    """Sync all user subscriptions with Beag API"""
    sync_service = SubscriptionSyncService()
    result = await sync_service.sync_all_users()
    return result


async def background_worker():
    """Background worker that runs subscription sync every SYNC_INTERVAL_HOURS"""
    logger.info(f"Starting background subscription sync worker (interval: {settings.sync_interval_hours} hours)")
    
    while not should_stop_worker:
        logger.info(f"Starting subscription sync at {datetime.now()}")
        
        try:
            result = await sync_subscriptions()
            logger.info(f"Subscription sync completed: {result}")
        except Exception as e:
            logger.error(f"Error during sync: {str(e)}")
        
        # Wait for next sync interval (check should_stop_worker every 60 seconds)
        sleep_seconds = settings.sync_interval_hours * 3600
        logger.info(f"Next sync in {settings.sync_interval_hours} hours")
        
        # Sleep in chunks so we can check should_stop_worker periodically
        total_sleep = 0
        while total_sleep < sleep_seconds and not should_stop_worker:
            await asyncio.sleep(min(60, sleep_seconds - total_sleep))
            total_sleep += 60
    
    logger.info("Background worker stopped")


@app.on_event("startup")
async def startup_event():
    global background_task
    logger.info(f"Starting Beag Boilerplate Backend in {settings.environment} mode")
    logger.info(f"CORS origins: {settings.cors_origins}")
    
    # Start background worker
    background_task = asyncio.create_task(background_worker())
    logger.info("Background worker started")


@app.on_event("shutdown")
async def shutdown_event():
    global should_stop_worker, background_task
    logger.info("Shutting down Beag Boilerplate Backend")
    
    # Stop background worker gracefully
    should_stop_worker = True
    if background_task:
        logger.info("Stopping background worker...")
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            logger.info("Background worker cancelled")