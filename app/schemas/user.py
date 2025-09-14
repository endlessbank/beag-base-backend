from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    subscription_status: Optional[str] = None
    plan_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    my_saas_app_id: Optional[str] = None
    beag_client_id: Optional[int] = None


class User(UserBase):
    id: int
    beag_client_id: Optional[int] = None
    subscription_status: Optional[str] = None
    plan_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    my_saas_app_id: Optional[str] = None
    last_synced: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class UserInDB(User):
    pass