from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    beag_client_id = Column(Integer, nullable=True)
    
    # Subscription data from Beag
    subscription_status = Column(String, nullable=True)  # PAID, CANCELLED, FAILED, etc.
    plan_id = Column(Integer, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    my_saas_app_id = Column(String, nullable=True)
    
    # Tracking
    last_synced = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())