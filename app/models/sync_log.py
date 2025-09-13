from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class SyncLog(Base):
    __tablename__ = "sync_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    users_synced = Column(Integer, default=0)
    users_failed = Column(Integer, default=0)
    status = Column(String, nullable=False)  # SUCCESS, PARTIAL, FAILED
    error_message = Column(Text, nullable=True)