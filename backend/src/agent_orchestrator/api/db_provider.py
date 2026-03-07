"""Shared database provider for API routes.

All route modules should use get_db() from this module instead of
maintaining their own module-level DatabaseManager instances.
"""

from __future__ import annotations

from agent_orchestrator.storage import DatabaseManager

_db: DatabaseManager | None = None


def _init_db() -> None:
    """(Re)initialise the shared in-memory database."""
    global _db  # noqa: PLW0603
    if _db is not None:
        _db.close()
    _db = DatabaseManager(":memory:", check_same_thread=False)
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
