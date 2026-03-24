# backend/config/settings.py

"""
SentinelAI Settings Loader
Loads environment variables securely
"""

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

class Settings:

    # -------------------------
    # APP
    # -------------------------
    APP_NAME = os.getenv("APP_NAME", "SentinelAI")
    APP_ENV = os.getenv("APP_ENV", "development")

    # -------------------------
    # JWT
    # -------------------------
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "sentinel_jwt_secret"
    )

    JWT_REFRESH_SECRET_KEY = os.getenv(
        "JWT_REFRESH_SECRET_KEY",
        "sentinel_refresh_secret"
    )

    JWT_ALGORITHM = os.getenv(
        "JWT_ALGORITHM",
        "HS256"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            60
        )
    )

    REFRESH_TOKEN_EXPIRE_DAYS = int(
        os.getenv(
            "REFRESH_TOKEN_EXPIRE_DAYS",
            7
        )
    )

    # -------------------------
    # API KEYS
    # -------------------------
    CCTV_API_KEY = os.getenv(
        "CCTV_API_KEY",
        "sentinel_cctv_key"
    )

    EXAM_API_KEY = os.getenv(
        "EXAM_API_KEY",
        "sentinel_exam_key"
    )

    LMS_API_KEY = os.getenv(
        "LMS_API_KEY",
        "sentinel_lms_key"
    )

    # -------------------------
    # LOGGING
    # -------------------------
    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )

settings = Settings()
