# backend/auth/jwt_handler.py

"""
SentinelAI JWT Authentication Handler
-------------------------------------

Production-ready JWT authentication system.

Features:
- Access Token
- Refresh Token
- Expiry
- Role-based payload
- Secure secret from .env via settings
- Token verification
- Logging
- FastAPI compatible
- Token pair generation
- Refresh token support
- Secure algorithm handling

Usage:

    from auth.jwt_handler import create_access_token

    token = create_access_token(
        user_id="admin",
        role="admin"
    )

Header:

    Authorization: Bearer <token>
"""

import jwt
import logging
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from backend.config.settings import settings

# -----------------------------
# LOGGING
# -----------------------------
logger = logging.getLogger("SentinelAI.JWT")

# -----------------------------
# CONFIG FROM ENV
# -----------------------------
SECRET_KEY = settings.JWT_SECRET_KEY
REFRESH_SECRET = settings.JWT_REFRESH_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# -----------------------------
# CREATE ACCESS TOKEN
# -----------------------------
def create_access_token(user_id: str, role: str):
    """
    Create JWT access token
    """

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow()
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    logger.info(f"Access token created for {user_id}")

    return token

# -----------------------------
# CREATE REFRESH TOKEN
# -----------------------------
def create_refresh_token(user_id: str):
    """
    Create refresh token
    """

    expire = datetime.utcnow() + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow()
    }

    token = jwt.encode(
        payload,
        REFRESH_SECRET,
        algorithm=ALGORITHM
    )

    logger.info(f"Refresh token created for {user_id}")

    return token

# -----------------------------
# VERIFY ACCESS TOKEN
# -----------------------------
def verify_access_token(token: str):
    """
    Verify access token
    """

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":

            logger.warning("Invalid token type")

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        logger.info(
            f"Token verified for user: {payload.get('sub')}"
        )

        return payload

    except jwt.ExpiredSignatureError:

        logger.warning("Access token expired")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    except jwt.InvalidTokenError:

        logger.warning("Invalid access token")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# -----------------------------
# VERIFY REFRESH TOKEN
# -----------------------------
def verify_refresh_token(token: str):
    """
    Verify refresh token
    """

    try:

        payload = jwt.decode(
            token,
            REFRESH_SECRET,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":

            logger.warning("Invalid refresh token type")

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        logger.info(
            f"Refresh token verified for user: {payload.get('sub')}"
        )

        return payload

    except jwt.ExpiredSignatureError:

        logger.warning("Refresh token expired")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )

    except jwt.InvalidTokenError:

        logger.warning("Invalid refresh token")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

# -----------------------------
# CREATE TOKEN PAIR
# -----------------------------
def create_token_pair(user_id: str, role: str):
    """
    Create access + refresh token pair
    """

    access_token = create_access_token(user_id, role)
    refresh_token = create_refresh_token(user_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# -----------------------------
# REFRESH ACCESS TOKEN
# -----------------------------
def refresh_access_token(refresh_token: str):
    """
    Generate new access token using refresh token
    """

    payload = verify_refresh_token(refresh_token)

    user_id = payload["sub"]

    new_access_token = create_access_token(
        user_id=user_id,
        role="admin"
    )

    logger.info(f"Access token refreshed for {user_id}")

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
