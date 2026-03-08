"""Application configuration loaded from environment variables (T-113).

Usage::

    from agent_orchestrator.config import get_config

    cfg = get_config()
    print(cfg.db_path, cfg.port)
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

_DEFAULT_DB_PATH = "~/.agent-orchestrator/orchestrator.db"
_DEFAULT_HOST = "0.0.0.0"
_DEFAULT_PORT = 8000
_DEFAULT_DEV_MODE = False
_DEFAULT_OLLAMA_URL = "http://localhost:11434"
_DEFAULT_LOG_DIR = "~/.agent-orchestrator/logs"
_DEFAULT_PERSONALITIES_PATH = "config/personalities.json"

_TRUTHY = {"1", "true", "yes"}


# ---------------------------------------------------------------------------
# Config dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""

    db_path: str
    host: str
    port: int
    dev_mode: bool
    ollama_url: str
    log_dir: str
    personalities_path: str

    @classmethod
    def from_env(cls) -> AppConfig:
        """Build config from environment variables with sensible defaults."""
        return cls(
            db_path=os.path.expanduser(
                os.environ.get("DB_PATH", _DEFAULT_DB_PATH)
            ),
            host=os.environ.get("HOST", _DEFAULT_HOST),
            port=int(os.environ.get("PORT", str(_DEFAULT_PORT))),
            dev_mode=os.environ.get("DEV_MODE", "").lower() in _TRUTHY,
            ollama_url=os.environ.get("OLLAMA_URL", _DEFAULT_OLLAMA_URL),
            log_dir=os.path.expanduser(
                os.environ.get("LOG_DIR", _DEFAULT_LOG_DIR)
            ),
            personalities_path=os.environ.get(
                "PERSONALITIES_PATH", _DEFAULT_PERSONALITIES_PATH
            ),
        )


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------

_config: AppConfig | None = None


def get_config() -> AppConfig:
    """Return the cached application configuration singleton."""
    global _config  # noqa: PLW0603
    if _config is None:
        _config = AppConfig.from_env()
    return _config
