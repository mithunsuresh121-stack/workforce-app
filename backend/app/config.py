# app/config.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

class Settings:
    # PostgreSQL settings
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "workforce")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "workforce_pw")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "workforce")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")  # Use localhost for local PostgreSQL
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))

    # JWT / App settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
    APP_ENV: str = os.getenv("APP_ENV", "dev")


# Load settings
settings = Settings()

# Construct the database URL - using Unix socket since PostgreSQL is running on /tmp
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
