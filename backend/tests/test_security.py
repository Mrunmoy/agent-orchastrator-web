"""Tests for local auth token and rate limiter (OPS-001)."""

from __future__ import annotations

import time
from unittest.mock import patch

from agent_orchestrator.api.security import (
    AuthConfig,
    RateLimiter,
    TokenValidator,
    generate_token,
)

# ---------------------------------------------------------------------------
# TokenValidator tests
# ---------------------------------------------------------------------------


class TestTokenValidatorDisabled:
    """When auth is disabled (token=None), all requests pass."""

    def test_returns_true_for_none_token(self) -> None:
        config = AuthConfig(token=None)
        validator = TokenValidator(config)
        assert validator.validate(None) is True

    def test_returns_true_for_any_token(self) -> None:
        config = AuthConfig(token=None)
        validator = TokenValidator(config)
        assert validator.validate("anything") is True

    def test_is_enabled_false(self) -> None:
        config = AuthConfig(token=None)
        validator = TokenValidator(config)
        assert validator.is_enabled() is False


class TestTokenValidatorEnabled:
    """When auth is enabled (token set), validate properly."""

    def setup_method(self) -> None:
        self.secret = "test-secret-token-abc123"
        self.config = AuthConfig(token=self.secret)
        self.validator = TokenValidator(self.config)

    def test_rejects_none(self) -> None:
        assert self.validator.validate(None) is False

    def test_rejects_wrong_token(self) -> None:
        assert self.validator.validate("wrong-token") is False

    def test_accepts_correct_token(self) -> None:
        assert self.validator.validate(self.secret) is True

    def test_is_enabled_true(self) -> None:
        assert self.validator.is_enabled() is True

    def test_uses_constant_time_comparison(self) -> None:
        """Ensure secrets.compare_digest is used, not == operator."""
        with patch(
            "agent_orchestrator.api.security.secrets.compare_digest", return_value=True
        ) as mock_cmp:
            self.validator.validate("some-token")
            mock_cmp.assert_called_once()


# ---------------------------------------------------------------------------
# RateLimiter tests
# ---------------------------------------------------------------------------


class TestRateLimiter:
    def test_allows_under_limit(self) -> None:
        limiter = RateLimiter(max_rpm=5)
        for _ in range(5):
            assert limiter.check("client-a") is True

    def test_blocks_over_limit(self) -> None:
        limiter = RateLimiter(max_rpm=3)
        for _ in range(3):
            limiter.check("client-a")
        assert limiter.check("client-a") is False

    def test_sliding_window_expires_old_entries(self) -> None:
        limiter = RateLimiter(max_rpm=2)
        # Inject old timestamps directly to simulate time passing
        now = time.monotonic()
        limiter._requests["client-a"] = [now - 61, now - 61]
        # Old entries should be pruned, so new request is allowed
        assert limiter.check("client-a") is True

    def test_reset_clears_single_client(self) -> None:
        limiter = RateLimiter(max_rpm=2)
        limiter.check("client-a")
        limiter.check("client-b")
        limiter.reset("client-a")
        # client-a should be cleared, client-b untouched
        assert limiter.check("client-a") is True
        # Verify client-b still has its entry
        assert len(limiter._requests.get("client-b", [])) == 1

    def test_reset_all(self) -> None:
        limiter = RateLimiter(max_rpm=2)
        limiter.check("client-a")
        limiter.check("client-b")
        limiter.reset()
        assert limiter._requests == {}


# ---------------------------------------------------------------------------
# generate_token tests
# ---------------------------------------------------------------------------


class TestGenerateToken:
    def test_returns_unique_tokens(self) -> None:
        tokens = {generate_token() for _ in range(10)}
        assert len(tokens) == 10

    def test_returns_proper_length(self) -> None:
        token = generate_token()
        # secrets.token_urlsafe(32) produces 43 chars
        assert len(token) == 43


# ---------------------------------------------------------------------------
# AuthConfig defaults
# ---------------------------------------------------------------------------


class TestAuthConfig:
    def test_defaults(self) -> None:
        config = AuthConfig()
        assert config.token is None
        assert config.rate_limit_rpm == 120
