"""
Application configuration using pydantic-settings.
Loads settings from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    MONGODB_URI: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI",
    )
    DB_NAME: str = Field(
        default="dark_pattern_detector",
        description="MongoDB database name",
    )
    ML_MODEL_PATH: str = Field(
        default="ml/models/dark_pattern_model.joblib",
        description="Path to the trained ML model file",
    )
    HOST: str = Field(
        default="0.0.0.0",
        description="Server host",
    )
    PORT: int = Field(
        default=8000,
        description="Server port",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Singleton settings instance
settings = Settings()
