# backend/auth/auth_handler.py

"""
SentinelAI Authentication Handler
---------------------------------

Handles:

- JWT Authentication
- Role-based access
- Admin validation
- API Key validation
- WebSocket authentication
- Secure header parsing
- Logging
- Production-grade security checks

Compatible with:

- Exam Portal
- LMS
- CCTV
- Admin Dashboard
- External platforms
"""

import logging
from typing import Optional, Dict, Any

from fastapi import Header, HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.auth.jwt_handler import verify_access_token
from backend.auth.api_key import verify_api_key

# -----------------------------
# LOGGING
# -----------------------------
logger = logging.getLogger("SentinelAI.Auth")

# -----------------------------
# SECURITY
# -----------------------------
bearer_scheme = HTTPBearer(auto_error=False)

# -----------------------------
# ROLE CONSTANTS
# -----------------------------
ROLE_ADMIN = "admin"
ROLE_EXAM = "exam"
ROLE_LMS = "lms"
ROLE_CCTV = "cctv"

ALLOWED_EXAM_ROLES = [ROLE_ADMIN, ROLE_EXAM]
ALLOWED_LMS_ROLES = [ROLE_ADMIN, ROLE_LMS]
ALLOWED_SECURE_ROLES = [ROLE_ADMIN, ROLE_EXAM, ROLE_LMS, ROLE_CCTV]

# -----------------------------
# JWT AUTH
# -----------------------------
def jwt_auth(
    authorization: Optional[str] = Header(
        None,
        alias="Authorization"
    )
) -> Dict[str, Any]:
    """
    JWT Authentication dependency

    Reads Authorization header
    Validates Bearer token
    Returns decoded payload
    """

    if not authorization:

        logger.warning("Authorization header missing")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    if not authorization.startswith("Bearer "):

        logger.warning("Invalid authorization format")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Use Bearer token"
        )

    try:

        token = authorization.split(" ")[1].strip()

        if not token:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing"
            )

        payload = verify_access_token(token)

        logger.info(
            f"Authenticated user: {payload.get('sub')} | role: {payload.get('role')}"
        )

        return payload

    except HTTPException:
        raise

    except Exception as e:

        logger.error(f"JWT authentication failed: {e}")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

# -----------------------------
# ADMIN AUTH
# -----------------------------
def admin_auth(
    authorization: Optional[str] = Header(
        None,
        alias="Authorization"
    )
) -> Dict[str, Any]:
    """
    Admin-only access
    """

    payload = jwt_auth(authorization)

    role = payload.get("role")

    if role != ROLE_ADMIN:

        logger.warning(
            f"Unauthorized admin access attempt by {payload.get('sub')} with role {role}"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    logger.info(
        f"Admin access granted to {payload.get('sub')}"
    )

    return payload

# -----------------------------
# EXAM PORTAL AUTH
# -----------------------------
def exam_auth(
    authorization: Optional[str] = Header(
        None,
        alias="Authorization"
    )
) -> Dict[str, Any]:
    """
    Exam portal access
    """

    payload = jwt_auth(authorization)

    role = payload.get("role")

    if role not in ALLOWED_EXAM_ROLES:

        logger.warning(
            f"Unauthorized exam access attempt by {payload.get('sub')} role {role}"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Exam portal access required"
        )

    logger.info(
        f"Exam access granted to {payload.get('sub')}"
    )

    return payload

# -----------------------------
# LMS AUTH
# -----------------------------
def lms_auth(
    authorization: Optional[str] = Header(
        None,
        alias="Authorization"
    )
) -> Dict[str, Any]:
    """
    LMS access
    """

    payload = jwt_auth(authorization)

    role = payload.get("role")

    if role not in ALLOWED_LMS_ROLES:

        logger.warning(
            f"Unauthorized LMS access attempt by {payload.get('sub')} role {role}"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="LMS access required"
        )

    logger.info(
        f"LMS access granted to {payload.get('sub')}"
    )

    return payload

# -----------------------------
# CCTV AUTH (API KEY)
# -----------------------------
def cctv_auth(
    x_api_key: Optional[str] = Header(
        None,
        alias="X-API-Key"
    )
) -> Dict[str, Any]:
    """
    CCTV API key authentication
    """

    if not x_api_key:

        logger.warning("CCTV API key missing")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing"
        )

    try:

        result = verify_api_key(x_api_key)

        logger.info("CCTV API key authenticated")

        return result

    except HTTPException:
        raise

    except Exception as e:

        logger.error(f"CCTV authentication failed: {e}")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

# -----------------------------
# COMBINED AUTH
# -----------------------------
def secure_auth(
    authorization: Optional[str] = Header(
        None,
        alias="Authorization"
    ),
    x_api_key: Optional[str] = Header(
        None,
        alias="X-API-Key"
    )
) -> Dict[str, Any]:
    """
    Accepts either JWT or API key

    Used for:

    - evidence access
    - events
    - monitoring
    - integrations
    """

    if authorization:

        logger.info("Using JWT authentication")

        return jwt_auth(authorization)

    if x_api_key:

        logger.info("Using API key authentication")

        return verify_api_key(x_api_key)

    logger.warning("Authentication required")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )

# -----------------------------
# WEBSOCKET AUTH
# -----------------------------
async def websocket_auth(websocket: WebSocket) -> Optional[Dict[str, Any]]:
    """
    Authenticate WebSocket connection

    Usage:

    ws://localhost:8000/ws/streams?token=jwt_token
    """

    token = websocket.query_params.get("token")

    if not token:

        logger.warning("WebSocket token missing")

        await websocket.close(code=1008)
        return None

    try:

        payload = verify_access_token(token)

        logger.info(
            f"WebSocket connected: {payload.get('sub')} role: {payload.get('role')}"
        )

        return payload

    except HTTPException:

        logger.warning("WebSocket token invalid")

        await websocket.close(code=1008)
        return None

    except Exception as e:

        logger.error(f"WebSocket auth error: {e}")

        await websocket.close(code=1008)
        return None
