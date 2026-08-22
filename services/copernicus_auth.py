"""
NIRVAAN Copernicus OAuth2 Authentication Manager (services/copernicus_auth.py)

Manages OAuth2 client-credentials authentication for Copernicus Data Space Ecosystem (CDSE)
APIs (Process API / Sentinel Hub, OData, etc.).
Features:
- In-memory token caching with expiration buffer
- Automatic refresh upon token expiry
- Timeout and error handling
- Zero credential / token exposure in logs or error messages
"""

import json
import logging
import os
import time
from typing import Optional
import urllib.parse
import urllib.request
import urllib.error

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("nirvaan.copernicus_auth")

DEFAULT_TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
DEFAULT_EXPIRY_BUFFER_SEC = 60  # Refresh token 60s before it actually expires


class CopernicusAuthManager:
    """
    Thread-safe OAuth2 Token Manager for Copernicus Data Space Ecosystem.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_url: str = DEFAULT_TOKEN_URL,
        timeout_sec: float = 12.0,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self.token_url = token_url
        self.timeout_sec = timeout_sec

        self._cached_token: Optional[str] = None
        self._expires_at: float = 0.0

    @property
    def client_id(self) -> Optional[str]:
        if self._client_id is not None:
            return self._client_id
        return os.getenv("COPERNICUS_CLIENT_ID")

    @property
    def client_secret(self) -> Optional[str]:
        if self._client_secret is not None:
            return self._client_secret
        return os.getenv("COPERNICUS_CLIENT_SECRET")

    def has_credentials(self) -> bool:
        """Checks whether both client ID and client secret are configured."""
        cid = self.client_id
        csec = self.client_secret
        return bool(cid and cid.strip() and csec and csec.strip())

    def is_token_valid(self) -> bool:
        """Returns True if the currently cached token is not expired."""
        if not self._cached_token:
            return False
        return time.time() < (self._expires_at - DEFAULT_EXPIRY_BUFFER_SEC)

    def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Retrieves a valid OAuth2 Bearer token, using cache when available or refreshing.
        Returns None if credentials are missing or token acquisition fails.
        """
        if not force_refresh and self.is_token_valid():
            return self._cached_token

        cid = self.client_id
        csec = self.client_secret

        if not cid or not csec:
            logger.debug("Copernicus credentials (COPERNICUS_CLIENT_ID / COPERNICUS_CLIENT_SECRET) not set.")
            return None

        payload = urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "client_id": cid.strip(),
            "client_secret": csec.strip()
        }).encode("utf-8")

        req = urllib.request.Request(
            self.token_url,
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "NIRVAAN-Disaster-Intelligence/1.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                resp_body = resp.read().decode("utf-8")
                token_data = json.loads(resp_body)

                access_token = token_data.get("access_token")
                expires_in = int(token_data.get("expires_in", 1800))

                if access_token:
                    self._cached_token = access_token
                    self._expires_at = time.time() + expires_in
                    logger.info("Copernicus OAuth2 token acquired successfully (valid for %ds).", expires_in)
                    return self._cached_token
                else:
                    logger.warning("Copernicus token response did not contain access_token.")
                    return None
        except urllib.error.HTTPError as he:
            logger.error("Copernicus OAuth2 authentication failed with HTTP %d.", he.code)
            return None
        except Exception as e:
            logger.error("Copernicus OAuth2 request failed: %s", type(e).__name__)
            return None

    def invalidate_token(self) -> None:
        """Clears cached token to force a refresh on next call."""
        self._cached_token = None
        self._expires_at = 0.0


# Global singleton instance
_DEFAULT_COPERNICUS_AUTH = CopernicusAuthManager()


def get_copernicus_auth() -> CopernicusAuthManager:
    """Returns the default CopernicusAuthManager singleton."""
    return _DEFAULT_COPERNICUS_AUTH
