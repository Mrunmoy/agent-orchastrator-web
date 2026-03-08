"""Shared database provider for API routes.

All route modules should use get_db() from this module instead of
maintaining their own module-level DatabaseManager instances.
"""

from __future__ import annotations

import os

from agent_orchestrator.config import get_config
from agent_orchestrator.storage import DatabaseManager

_db: DatabaseManager | None = None


def _init_db() -> None:
    """(Re)initialise the shared database from config."""
    global _db  # noqa: PLW0603
    if _db is not None:
        _db.close()
    cfg = get_config()
    db_dir = os.path.dirname(cfg.db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    _db = DatabaseManager(cfg.db_path, check_same_thread=False)
    _db.initialize()


def get_db() -> DatabaseManager:
    """Return the shared DatabaseManager, initialising if needed."""
    global _db  # noqa: PLW0603
    if _db is None:
        _init_db()
    assert _db is not None
    return _db


# Eagerly initialise on import so routes work immediately.
_init_db()
