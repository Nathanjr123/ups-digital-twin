"""
Core Configuration
Application settings and configuration management.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    app_name: str = "UPS Digital Twin API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"
    debug: bool = True
    
    # CORS
    cors_origins: list[str] = ["*"]
    
    # Data Generation
    fleet_size: int = 12
    telemetry_update_interval: int = 2  # seconds
    
    # ML Models
    models_dir: str = "./models"
    training_data_days: int = 90
    
    # WebSocket
    ws_heartbeat_interval: int = 30  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
