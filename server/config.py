from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    DATABASE_PATH: str = "medical.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    HASH_ROUNDS: int = 12
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()