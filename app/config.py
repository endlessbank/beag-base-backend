from pydantic import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Beag API Configuration
    beag_api_key: str
    beag_api_url: str = "https://my-saas-basic-api-d5e3hpgdf0gnh2em.eastus-01.azurewebsites.net/api/v1/saas"
    
    # Database
    database_url: str
    
    # CORS Configuration
    frontend_url: str = "http://localhost:3000"
    admin_url: str = "http://localhost:3001"
    
    # Server
    port: int = 8000
    environment: str = "development"
    
    # Worker Configuration
    sync_interval_hours: int = 6
    
    @property
    def cors_origins(self) -> List[str]:
        return [self.frontend_url, self.admin_url]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()