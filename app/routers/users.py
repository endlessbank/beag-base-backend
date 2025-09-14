from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging
from app.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate
from app.services.beag_client import BeagClient
from app.services.sync_service import SubscriptionSyncService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)


@router.post("/", response_model=UserSchema)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user and sync their subscription data"""
    logger.info(f"🔍 [DEBUG] POST /api/users/ called with email: {user.email}")
    
    # Check if user already exists
    logger.info(f"🔍 [DEBUG] Checking if user already exists: {user.email}")
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.info(f"✅ [DEBUG] User already exists, syncing and returning: {user.email} (ID: {existing_user.id})")
        # Instead of failing, sync and return the existing user
        sync_service = SubscriptionSyncService()
        await sync_service.sync_user(db, existing_user)
        return existing_user
    
    logger.info(f"🔍 [DEBUG] User does not exist, creating new user: {user.email}")
    try:
        # Create user
        logger.info(f"🔍 [DEBUG] Creating User object and adding to database")
        db_user = User(email=user.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"✅ [DEBUG] User created successfully in database: {user.email} (ID: {db_user.id})")
        
        # Sync subscription data
        logger.info(f"🔍 [DEBUG] Starting subscription sync for new user: {user.email}")
        sync_service = SubscriptionSyncService()
        await sync_service.sync_user(db, db_user)
        logger.info(f"✅ [DEBUG] User creation and sync completed: {user.email}")
        
        return db_user
    except Exception as e:
        logger.error(f"❌ [DEBUG] Error creating user {user.email}: {str(e)}")
        db.rollback()
        # Check again if user was created by another process
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            logger.info(f"🔍 [DEBUG] User was created by another process during error, returning: {user.email}")
            # User was created by another process, sync and return it
            sync_service = SubscriptionSyncService()
            await sync_service.sync_user(db, existing_user)
            return existing_user
        else:
            # Real error, re-raise
            logger.error(f"❌ [DEBUG] Failed to create user, no existing user found: {user.email}")
            raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.get("/", response_model=List[UserSchema])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/by-email/{email}", response_model=UserSchema)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """Get user by email"""
    logger.info(f"🔍 [DEBUG] GET /api/users/by-email/{email} called")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.info(f"❌ [DEBUG] User not found in database: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"✅ [DEBUG] User found in database: {email} (ID: {user.id})")
    return user


@router.post("/sync/{user_id}")
async def sync_user_subscription(user_id: int, db: Session = Depends(get_db)):
    """Manually sync a user's subscription data"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    sync_service = SubscriptionSyncService()
    success = await sync_service.sync_user(db, user)
    
    if success:
        return {"message": "Subscription synced successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to sync subscription")