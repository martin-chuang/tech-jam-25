"""Configuration loader utility."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class AppConfig:
    """Application configuration class."""

    # Database Configuration
    db_host: str
    db_port: int
    db_username: str
    db_password: Optional[str]
    db_database: str

    # Application Configuration
    port: int
    debug: bool

    # Redis Configuration
    redis_host: str
    redis_port: int

    # Security
    secret_key: str


class ConfigLoader:
    @staticmethod
    def load_config() -> AppConfig:
        """Load configuration from environment variables."""
        # Load environment variables from the appropriate .env file
        env = os.getenv("FLASK_ENV", "development")
        load_dotenv(f".env.{env}")

        return AppConfig(
            # Database Configuration
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_username=os.getenv("DB_USERNAME", "postgres"),
            db_password=os.getenv("DB_PASSWORD"),
            db_database=os.getenv("DB_DATABASE", "tiktok_techjam"),
            # Application Configuration
            port=int(os.getenv("PORT", "5000")),
            debug=os.getenv("DEBUG", "True").lower() == "true",
            # Redis Configuration
            redis_host=os.getenv("REDIS_HOST", "redis"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            # Security
            secret_key=os.getenv("SECRET_KEY", "dev-secret-key"),
        )


# Global config instance
config = ConfigLoader.load_config()
