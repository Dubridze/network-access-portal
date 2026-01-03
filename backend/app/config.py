from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Keycloak Configuration
    KEYCLOAK_SERVER_URL: str = "http://keycloak:8080"
    KEYCLOAK_REALM: str = "network-access"
    KEYCLOAK_CLIENT_ID: str = "network-portal"
    KEYCLOAK_CLIENT_SECRET: str = "your-client-secret"
    KEYCLOAK_ADMIN_USERNAME: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = "admin"

    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:password@postgres:5432/network_access_portal"
    DATABASE_HOST: str = "postgres"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "network_access_portal"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "password"
    SQLALCHEMY_ECHO: bool = False

    # Backend Configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@company.com"

    # Customization
    APP_TITLE: str = "Network Access Portal"
    APP_LOGO_URL: str = "/logo.png"
    APP_THEME_COLOR: str = "#1976d2"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
