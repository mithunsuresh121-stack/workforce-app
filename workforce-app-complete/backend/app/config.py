# app/config.py
from pydantic_settings import BaseSettings
from pydantic import validator
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

class Settings(BaseSettings):
    # PostgreSQL settings
    POSTGRES_USER: str = "workforce"
    POSTGRES_PASSWORD: str = "workforce_pw"
    POSTGRES_DB: str = "workforce"
    POSTGRES_HOST: str = "localhost"  # Use localhost for local PostgreSQL
    POSTGRES_PORT: int = 5432

    # Database URL
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # JWT / App settings
    SECRET_KEY: str = "CHANGE_ME"
    JWT_SECRET: str = "CHANGE_ME"
    JWT_REFRESH_SECRET: str = "CHANGE_ME_REFRESH"
    JWT_ALG: str = "HS256"
    APP_ENV: str = "dev"

    # Email settings
    SMTP_SERVER: str = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "apikey"
    SMTP_PASSWORD: str = ""  # Set in .env
    EMAIL_FROM: str = "noreply@workforceapp.com"
    SENDGRID_API_KEY: str = ""  # Set in .env (required for prod email)

    @validator('SENDGRID_API_KEY', pre=True, always=True)
    def validate_sendgrid_key(cls, v):
        if not v and os.getenv('APP_ENV') == 'prod':
            raise ValueError('SENDGRID_API_KEY is required in production')
        return v

    class Config:
        env_file = ".env"

# Load settings from .env
settings = Settings()

# Construct the database URL - using Unix socket since PostgreSQL is running on /tmp
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
