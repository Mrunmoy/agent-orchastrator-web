"""Standard API response envelope helpers."""

from __future__ import annotations

from typing import Any


def ok_response(data: dict[str, Any]) -> dict[str, Any]:
    """Wrap data in the standard ok envelope."""
    return {"ok": True, "data": data}


def error_response(message: str) -> dict[str, Any]:
    """Wrap an error message in the standard error envelope."""
    return {"ok": False, "error": message}
