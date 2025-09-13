from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate
from app.services.beag_client import BeagClient
from app.services.sync_service import SubscriptionSyncService

router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)


@router.post("/", response_model=UserSchema)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user and sync their subscription data"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        # Instead of failing, sync and return the existing user
        sync_service = SubscriptionSyncService()
        await sync_service.sync_user(db, existing_user)
        return existing_user
    
    try:
        # Create user
        db_user = User(email=user.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Sync subscription data
        sync_service = SubscriptionSyncService()
        await sync_service.sync_user(db, db_user)
        
        return db_user
    except Exception as e:
        db.rollback()
        # Check again if user was created by another process
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            # User was created by another process, sync and return it
            sync_service = SubscriptionSyncService()
            await sync_service.sync_user(db, existing_user)
            return existing_user
        else:
            # Real error, re-raise
            raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.get("/", response_model=List[UserSchema])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/by-email/{email}", response_model=UserSchema)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """Get user by email"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
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