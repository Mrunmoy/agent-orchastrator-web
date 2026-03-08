"""Base repository ABC (T-103).

Provides a minimal abstract base that all repository interfaces extend.
"""

from __future__ import annotations

from abc import ABC


class BaseRepository(ABC):
    """Marker base for all repository interfaces.

    Concrete implementations (SQLite, in-memory, etc.) will subclass the
    entity-specific repositories, which in turn extend this base.
    """
