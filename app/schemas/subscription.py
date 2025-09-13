from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


class SubscriptionStatus(str, Enum):
    PAID = "PAID"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    PAUSED = "PAUSED"
    RESUMED = "RESUMED"


class SubscriptionResponse(BaseModel):
    """Response from Beag API"""
    email: EmailStr
    status: SubscriptionStatus
    plan_id: int
    start_date: datetime
    end_date: datetime
    my_saas_app_id: str
    client_id: int