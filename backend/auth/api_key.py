# backend/auth/api_key.py

"""
SentinelAI API Key Authentication
---------------------------------

Production-ready API Key validation for:

- CCTV Systems
- LMS Platforms
- Exam Portals
- External Integrations

Features:
- Environment-based API keys
- Multiple API key support
- Role-based access
- Expiry support
- Secure header validation
- Logging
- Fallback keys
- settings.py integration
- Reload support
- Enterprise security validation

Usage:

    from auth.api_key import verify_api_key

    @app.get("/health")
    def health(api=Depends(verify_api_key)):
        return {"status": "ok"}

Header:

    X-API-Key: sentinel_cctv_key
"""

import os
import sys
import logging
import time
from fastapi import Header, HTTPException, status
from typing import Optional, Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from backend.config.settings import settings

# -----------------------------
# LOGGING
# -----------------------------
logger = logging.getLogger("SentinelAI.APIKey")

# -----------------------------
# DEFAULT KEYS (Fallback)
# -----------------------------
DEFAULT_API_KEYS = {
    "sentinel_cctv_key": {
        "role": "cctv",
        "name": "CCTV System",
        "expires": None
    },
    "sentinel_lms_key": {
        "role": "lms",
        "name": "LMS Platform",
        "expires": None
    },
    "sentinel_exam_key": {
        "role": "exam",
        "name": "Exam Portal",
        "expires": None
    }
}

# -----------------------------
# LOAD API KEYS FROM ENV
# -----------------------------
def load_api_keys() -> Dict[str, Any]:

    logger.info("Loading API keys")

    env_keys = os.getenv("SENTINEL_API_KEYS")

    # -----------------------------
    # settings.py fallback
    # -----------------------------
    if not env_keys:

        logger.warning("Using default API keys")

        keys = DEFAULT_API_KEYS.copy()

        # add keys from settings
        if settings.CCTV_API_KEY:
            keys[settings.CCTV_API_KEY] = {
                "role": "cctv",
                "name": "CCTV System",
                "expires": None
            }

        if settings.LMS_API_KEY:
            keys[settings.LMS_API_KEY] = {
                "role": "lms",
                "name": "LMS Platform",
                "expires": None
            }

        if settings.EXAM_API_KEY:
            keys[settings.EXAM_API_KEY] = {
                "role": "exam",
                "name": "Exam Portal",
                "expires": None
            }

        return keys

    keys = {}

    try:

        pairs = env_keys.split(",")

        for pair in pairs:

            parts = pair.split(":")

            if len(parts) < 2:
                continue

            key = parts[0].strip()
            role = parts[1].strip()

            expires = None

            if len(parts) == 3:
                expires = int(parts[2])

            keys[key] = {
                "role": role,
                "name": role,
                "expires": expires
            }

        logger.info("API keys loaded from environment")

        return keys

    except Exception as e:

        logger.error(f"Invalid API key format in ENV: {e}")

        return DEFAULT_API_KEYS

# -----------------------------
# INITIALIZE API KEYS
# -----------------------------
API_KEYS = load_api_keys()

# -----------------------------
# RELOAD KEYS
# -----------------------------
def reload_api_keys():
    global API_KEYS
    API_KEYS = load_api_keys()
    logger.info("API keys reloaded")

# -----------------------------
# VERIFY API KEY
# -----------------------------
def verify_api_key(
    x_api_key: Optional[str] = Header(
        None,
        alias="X-API-Key",
        description="API Key for external system access"
    )
) -> Dict[str, Any]:

    if not x_api_key:

        logger.warning("Missing API Key")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required"
        )

    if x_api_key not in API_KEYS:

        logger.warning(f"Invalid API Key attempt: {x_api_key}")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )

    key_data = API_KEYS[x_api_key]

    # -----------------------------
    # EXPIRY CHECK
    # -----------------------------
    expires = key_data.get("expires")

    if expires:

        if time.time() > expires:

            logger.warning(f"Expired API Key: {x_api_key}")

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API Key expired"
            )

    logger.info(
        f"Authorized API Key: {key_data['name']} role: {key_data['role']}"
    )

    return {
        "api_key": x_api_key,
        "role": key_data["role"],
        "name": key_data["name"]
    }

# -----------------------------
# ROLE-BASED ACCESS
# -----------------------------
def require_role(required_role: str):
    """
    Role-based API access
    """

    def role_checker(
        api_data: Dict[str, Any] = verify_api_key()
    ):

        if api_data["role"] != required_role:

            logger.warning(
                f"Access denied for role {api_data['role']}"
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        logger.info(
            f"Role validated: {required_role}"
        )

        return api_data

    return role_checker

# -----------------------------
# MULTI ROLE ACCESS
# -----------------------------
def require_roles(roles: list):
    """
    Allow multiple roles
    """

    def role_checker(
        api_data: Dict[str, Any] = verify_api_key()
    ):

        if api_data["role"] not in roles:

            logger.warning(
                f"Access denied for role {api_data['role']}"
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return api_data

    return role_checker

# -----------------------------
# GET API KEY INFO
# -----------------------------
def get_api_key_info(api_key: str):

    if api_key in API_KEYS:
        return API_KEYS[api_key]

    return None
