import asyncio
import logging
from datetime import datetime
from app.services.sync_service import SubscriptionSyncService
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def sync_subscriptions():
    """Sync all user subscriptions with Beag API"""
    sync_service = SubscriptionSyncService()
    result = await sync_service.sync_all_users()
    return result


async def run_worker():
    """Run the sync worker every SYNC_INTERVAL_HOURS"""
    logger.info(f"Starting subscription sync worker (interval: {settings.sync_interval_hours} hours)")
    
    while True:
        logger.info(f"Starting subscription sync at {datetime.now()}")
        
        try:
            result = await sync_subscriptions()
            logger.info(f"Subscription sync completed: {result}")
        except Exception as e:
            logger.error(f"Error during sync: {str(e)}")
        
        # Wait for next sync interval
        sleep_seconds = settings.sync_interval_hours * 3600
        logger.info(f"Next sync in {settings.sync_interval_hours} hours")
        await asyncio.sleep(sleep_seconds)


if __name__ == "__main__":
    # Run initial sync immediately, then continue with scheduled syncs
    logger.info("Starting worker...")
    asyncio.run(run_worker())