from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Fraud Detection API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    API_V1_PREFIX: str = "/api/v1"
    API_KEY: str = "dev-key-12345"
    
    MODEL_PATH: str = "models/isolation_forest_model.pkl"
    SCALER_PATH: str = "models/scaler.pkl"
    METADATA_PATH: str = "models/model_metadata.json"
    
    DATABASE_URL: str = "postgresql://fraud_user:fraud_pass@localhost:5432/fraud_detection"
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_EXPIRATION: int = 3600
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
