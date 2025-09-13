import httpx
from typing import Optional
from app.config import settings
from app.schemas.subscription import SubscriptionResponse
import logging

logger = logging.getLogger(__name__)


class BeagClient:
    """Client for interacting with Beag API"""
    
    def __init__(self):
        self.base_url = settings.beag_api_url
        self.api_key = settings.beag_api_key
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def get_subscription_by_email(self, email: str) -> Optional[SubscriptionResponse]:
        """
        Get subscription details for a user by email
        
        Returns None if user not found or has no active subscription
        """
        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/clients/by-email/{email}"
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return SubscriptionResponse(**data)
                elif response.status_code == 404:
                    logger.info(f"No subscription found for email: {email}")
                    return None
                else:
                    logger.error(f"Error fetching subscription for {email}: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return None
                    
            except httpx.RequestError as e:
                logger.error(f"Request error for {email}: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error for {email}: {str(e)}")
                return None
    
    async def get_subscription_by_id(self, client_id: int) -> Optional[SubscriptionResponse]:
        """
        Get subscription details for a user by client ID
        
        Returns None if user not found or has no active subscription
        """
        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/clients/by-id/{client_id}"
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return SubscriptionResponse(**data)
                elif response.status_code == 404:
                    logger.info(f"No subscription found for client_id: {client_id}")
                    return None
                else:
                    logger.error(f"Error fetching subscription for client_id {client_id}: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return None
                    
            except httpx.RequestError as e:
                logger.error(f"Request error for client_id {client_id}: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error for client_id {client_id}: {str(e)}")
                return None