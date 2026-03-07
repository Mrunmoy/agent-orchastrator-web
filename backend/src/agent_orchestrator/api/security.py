"""Local auth token validation and rate limiting for control APIs (OPS-001).

Provides building blocks for securing LAN-accessible API endpoints:
- AuthConfig: configuration dataclass for auth settings
- TokenValidator: bearer token validation (disabled when token is None)
- RateLimiter: simple sliding-window rate limiter per client
- generate_token: secure random token generator
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass


@dataclass
class AuthConfig:
    """Configuration for local API authentication.

    Attributes:
        token: Bearer token for API access. None means auth is disabled.
        rate_limit_rpm: Maximum requests per minute per client.
    """

    token: str | None = None
    rate_limit_rpm: int = 120


class RateLimiter:
    """Simple sliding-window rate limiter.

    Tracks request timestamps per client and enforces a maximum
    number of requests per 60-second window.
    """

    def __init__(self, max_rpm: int = 120) -> None:
        self._max_rpm = max_rpm
        self._requests: dict[str, list[float]] = {}

    def check(self, client_id: str) -> bool:
        """Check if a request from *client_id* is allowed.

        Returns True if within limit, False if rate-limited.
        """
        now = time.monotonic()
        cutoff = now - 60.0

        timestamps = self._requests.get(client_id, [])
        # Prune entries older than 60 seconds
        timestamps = [t for t in timestamps if t > cutoff]

        if len(timestamps) >= self._max_rpm:
            self._requests[client_id] = timestamps
            return False

        timestamps.append(now)
        self._requests[client_id] = timestamps
        return True

    def reset(self, client_id: str | None = None) -> None:
        """Reset rate limit tracking.

        If *client_id* is given, reset only that client.
        Otherwise reset all clients.
        """
        if client_id is not None:
            self._requests.pop(client_id, None)
        else:
            self._requests.clear()


class TokenValidator:
    """Bearer token validator for local API auth.

    When auth is disabled (config.token is None), all requests are allowed.
    When enabled, tokens are compared using constant-time comparison.
    """

    def __init__(self, config: AuthConfig) -> None:
        self._config = config

    def validate(self, token: str | None) -> bool:
        """Validate a bearer token.

        Returns True if:
        - Auth is disabled (config.token is None), or
        - The provided token matches the configured token.
        """
        if self._config.token is None:
            return True
        if token is None:
            return False
        return secrets.compare_digest(token, self._config.token)

    def is_enabled(self) -> bool:
        """Return True if token auth is enabled."""
        return self._config.token is not None


def generate_token() -> str:
    """Generate a secure random URL-safe token."""
    return secrets.token_urlsafe(32)
