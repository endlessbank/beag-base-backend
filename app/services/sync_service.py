from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.sync_log import SyncLog
from app.services.beag_client import BeagClient
import logging

logger = logging.getLogger(__name__)


class SubscriptionSyncService:
    """Service for syncing user subscriptions with Beag API"""
    
    def __init__(self):
        self.beag_client = BeagClient()
    
    async def sync_user(self, db: Session, user: User) -> bool:
        """
        Sync a single user's subscription data
        
        Returns True if successful, False otherwise
        """
        try:
            # Fetch latest subscription from Beag
            subscription = await self.beag_client.get_subscription_by_email(user.email)
            
            if subscription:
                # Update user with subscription data
                user.subscription_status = subscription.status
                user.plan_id = subscription.plan_id
                user.start_date = subscription.start_date
                user.end_date = subscription.end_date
                user.my_saas_app_id = subscription.my_saas_app_id
                user.beag_client_id = subscription.client_id
                user.last_synced = datetime.utcnow()
                
                db.commit()
                
                # Log detailed sync information
                start_date_str = subscription.start_date.strftime("%Y-%m-%d") if subscription.start_date else "N/A"
                end_date_str = subscription.end_date.strftime("%Y-%m-%d") if subscription.end_date else "N/A"
                logger.info(f"✅ Updated user: {user.email} | Status: {subscription.status} | Plan: {subscription.plan_id} | Period: {start_date_str} to {end_date_str}")
                return True
            else:
                # User has no active subscription
                user.subscription_status = None
                user.plan_id = None
                user.start_date = None
                user.end_date = None
                user.last_synced = datetime.utcnow()
                
                db.commit()
                logger.info(f"🚫 Updated user: {user.email} | Status: NO_SUBSCRIPTION | Plan: None | Period: N/A to N/A")
                return True
                
        except Exception as e:
            logger.error(f"Error syncing user {user.email}: {str(e)}")
            db.rollback()
            return False
    
    async def sync_all_users(self) -> dict:
        """
        Sync all users' subscription data
        
        Returns a summary of the sync operation
        """
        db = SessionLocal()
        sync_log = SyncLog(status="IN_PROGRESS")
        db.add(sync_log)
        db.commit()
        
        users_synced = 0
        users_failed = 0
        active_subscriptions = 0
        inactive_subscriptions = 0
        
        try:
            # Get all users
            users = db.query(User).all()
            total_users = len(users)
            
            logger.info(f"🔄 Starting subscription sync for {total_users} users...")
            
            # Sync each user
            for user in users:
                success = await self.sync_user(db, user)
                if success:
                    users_synced += 1
                    # Count subscription types after sync
                    if user.subscription_status and user.subscription_status.upper() in ['PAID', 'ACTIVE', 'TRIAL']:
                        active_subscriptions += 1
                    else:
                        inactive_subscriptions += 1
                else:
                    users_failed += 1
            
            # Update sync log
            sync_log.completed_at = datetime.utcnow()
            sync_log.users_synced = users_synced
            sync_log.users_failed = users_failed
            
            if users_failed == 0:
                sync_log.status = "SUCCESS"
            elif users_synced > 0:
                sync_log.status = "PARTIAL"
            else:
                sync_log.status = "FAILED"
            
            db.commit()
            
            # Enhanced completion summary
            logger.info(f"🎯 Sync completed successfully!")
            logger.info(f"📊 Summary: {users_synced} users processed, {users_failed} failed")
            logger.info(f"📈 Active subscriptions: {active_subscriptions} | Inactive/None: {inactive_subscriptions}")
            if users_failed > 0:
                logger.warning(f"⚠️  {users_failed} users failed to sync - check logs above for details")
            
            return {
                "total_users": total_users,
                "users_synced": users_synced,
                "users_failed": users_failed,
                "status": sync_log.status
            }
            
        except Exception as e:
            logger.error(f"💥 Critical error during sync operation: {str(e)}")
            sync_log.completed_at = datetime.utcnow()
            sync_log.status = "FAILED"
            sync_log.error_message = str(e)
            db.commit()
            
            # Enhanced error summary
            logger.error(f"❌ Sync failed after processing {users_synced} users successfully")
            if users_synced > 0:
                logger.info(f"📊 Partial success: {users_synced} users were updated before failure")
            
            return {
                "total_users": users_synced + users_failed,
                "users_synced": users_synced,
                "users_failed": users_failed,
                "status": "FAILED",
                "error": str(e)
            }
        finally:
            db.close()