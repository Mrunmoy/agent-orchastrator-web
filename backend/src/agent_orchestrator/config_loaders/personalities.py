"""Personality profiles loader (T-114).

Reads ``config/personalities.json`` and provides structured access via
:class:`PersonalityProfile` dataclasses.

Usage::

    from agent_orchestrator.config_loaders.personalities import (
        load_personalities,
        get_personality,
    )

    profiles = load_personalities()          # uses default path from AppConfig
    dev = get_personality("software_developer")
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_TEMPERATURE = 0.7

# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PersonalityProfile:
    """A single personality profile for an agent."""

    key: str
    display_name: str
    system_prompt_fragments: list[str] = field(default_factory=list)
    temperature: float = _DEFAULT_TEMPERATURE
    behavioral_constraints: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

_cache: dict[str, PersonalityProfile] | None = None


def _clear_cache() -> None:
    """Reset the module-level cache. Intended for test teardown."""
    global _cache  # noqa: PLW0603
    _cache = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_personalities(path: str | None = None) -> dict[str, PersonalityProfile]:
    """Load personality profiles from a JSON file.

    Parameters
    ----------
    path:
        Filesystem path to the personalities JSON file.  When *None*, the
        value from :func:`~agent_orchestrator.config.get_config` is used.

    Returns
    -------
    dict[str, PersonalityProfile]
        Mapping of profile key to :class:`PersonalityProfile`.  Returns an
        empty dict if the file does not exist.
    """
    global _cache  # noqa: PLW0603
    if _cache is not None:
        return _cache

    if path is None:
        from agent_orchestrator.config import get_config

        path = get_config().personalities_path

    file = Path(path)
    if not file.is_file():
        logger.warning("Personalities file not found: %s", path)
        _cache = {}
        return _cache

    try:
        raw: dict[str, Any] = json.loads(file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to read personalities file %s: %s", path, exc)
        _cache = {}
        return _cache

    profiles: dict[str, PersonalityProfile] = {}
    for key, entry in raw.items():
        instruction = entry.get("instruction", [])
        if isinstance(instruction, str):
            instruction = [instruction]

        profiles[key] = PersonalityProfile(
            key=key,
            display_name=entry.get("label", key),
            system_prompt_fragments=instruction,
            temperature=float(entry.get("temperature", _DEFAULT_TEMPERATURE)),
            behavioral_constraints=list(entry.get("traits", [])),
        )

    _cache = profiles
    return _cache


def get_personality(key: str) -> PersonalityProfile | None:
    """Return a single personality profile by key, or *None* if not found.

    Returns *None* if :func:`load_personalities` has not been called yet or
    the key does not exist.
    """
    if _cache is None:
        return None
    return _cache.get(key)
