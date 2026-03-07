"""Tests for app configuration (including CORS defaults/overrides)."""

from __future__ import annotations

from fastapi.middleware.cors import CORSMiddleware

from agent_orchestrator.api import create_app


def _cors_kwargs(app) -> dict[str, object]:
    for middleware in app.user_middleware:
        if middleware.cls is CORSMiddleware:
            return middleware.kwargs
    raise AssertionError("CORSMiddleware not configured")


def test_cors_uses_safe_local_defaults(monkeypatch) -> None:
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    app = create_app()
    cors = _cors_kwargs(app)
    assert cors["allow_origins"] == ["http://127.0.0.1:5173", "http://localhost:5173"]


def test_cors_allows_env_override(monkeypatch) -> None:
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://192.168.1.10:5173,http://localhost:5173")
    app = create_app()
    cors = _cors_kwargs(app)
    assert cors["allow_origins"] == ["http://192.168.1.10:5173", "http://localhost:5173"]
