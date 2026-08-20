"""
NIRVAAN Authentication, Authorization & Token Security Module (utils/auth.py)

Provides production-grade:
- PBKDF2-SHA256 password hashing & constant-time verification
- JWT session token generation & verification
- FastAPI HTTP Bearer security dependencies & role-based access control (RBAC)
"""

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
import secrets
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

SECRET_KEY = os.getenv("NIRVAAN_JWT_SECRET", "nirvaan-production-secret-key-32-chars-long!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security_scheme = HTTPBearer(auto_error=False)


# 1. Password Hashing (PBKDF2-HMAC-SHA256)
def hash_password(password: str) -> str:
    """Hashes a plaintext password using PBKDF2-HMAC-SHA256 with random salt."""
    salt = secrets.token_bytes(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${derived.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a stored PBKDF2 hash using constant-time comparison."""
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        target_hash = bytes.fromhex(parts[3])
        derived = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, iterations)
        return hmac.compare_digest(derived, target_hash)
    except Exception:
        return False


# 2. JWT Generation & Verification
def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _base64url_decode(data_str: str) -> bytes:
    padding = '=' * (4 - len(data_str) % 4)
    return base64.urlsafe_b64decode((data_str + padding).encode('utf-8'))


def create_access_token(user_id: str, email: str, role: str = "user", expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token containing user identity and claims."""
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))

    header = {"alg": ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "NIRVAAN-Disaster-Intelligence"
    }

    header_b64 = _base64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = _base64url_encode(json.dumps(payload).encode('utf-8'))

    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a signed JWT token."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT token format")

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    actual_sig = _base64url_decode(sig_b64)

    if not hmac.compare_digest(expected_sig, actual_sig):
        raise ValueError("JWT signature verification failed")

    payload = json.loads(_base64url_decode(payload_b64).decode('utf-8'))
    now_ts = int(datetime.now(timezone.utc).timestamp())

    if payload.get("exp") and now_ts > payload["exp"]:
        raise ValueError("JWT token has expired")

    return payload


# 3. FastAPI Dependencies for Auth & RBAC
def get_current_user_from_header(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Extracts and verifies JWT token from Authorization header if present."""
    if not authorization:
        return None
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        return decode_access_token(token)
    except Exception:
        return None
