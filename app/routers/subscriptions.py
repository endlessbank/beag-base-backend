from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.subscription import SubscriptionResponse
from app.services.beag_client import BeagClient

router = APIRouter(
    prefix="/api/subscriptions",
    tags=["subscriptions"]
)


@router.get("/check/{email}", response_model=SubscriptionResponse)
async def check_subscription(email: str):
    """
    Check subscription status directly from Beag API
    This endpoint bypasses the local cache and gets real-time data
    """
    beag_client = BeagClient()
    subscription = await beag_client.get_subscription_by_email(email)
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    return subscription


@router.get("/cached/{email}")
def get_cached_subscription(email: str, db: Session = Depends(get_db)):
    """
    Get subscription status from local database (cached data)
    This is faster but may be up to 6 hours old
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.subscription_status:
        raise HTTPException(status_code=404, detail="No subscription data available")
    
    return {
        "email": user.email,
        "status": user.subscription_status,
        "plan_id": user.plan_id,
        "start_date": user.start_date,
        "end_date": user.end_date,
        "last_synced": user.last_synced
    }


@router.post("/sync-all")
async def trigger_sync_all():
    """
    Manually trigger a sync of all users' subscription data
    This is useful for admin operations
    """
    from app.services.sync_service import SubscriptionSyncService
    
    sync_service = SubscriptionSyncService()
    result = await sync_service.sync_all_users()
    
    return result