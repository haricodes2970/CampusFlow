from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Supabase Configuration
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    
    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,https://campusflowww.vercel.app,https://campusflow.vercel.app"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()