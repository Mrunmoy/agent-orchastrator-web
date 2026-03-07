"""Shared fixtures for end-to-end tests.

Uses httpx.AsyncClient with ASGITransport to test the FastAPI app
without starting a real server.
"""

from __future__ import annotations

import sys
from collections.abc import AsyncGenerator
from pathlib import Path

# Ensure the backend source tree is on sys.path so `agent_orchestrator`
# can be imported regardless of the working directory pytest is invoked from.
_BACKEND_SRC = str(Path(__file__).resolve().parents[2] / "backend" / "src")
if _BACKEND_SRC not in sys.path:
    sys.path.insert(0, _BACKEND_SRC)

import httpx  # noqa: E402
import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402

from agent_orchestrator.api import create_app  # noqa: E402
from agent_orchestrator.api.db_provider import _init_db  # noqa: E402


@pytest.fixture()
def app():
    """Return a fresh FastAPI application with a clean in-memory database."""
    _init_db()
    return create_app()


@pytest_asyncio.fixture()
async def client(app) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an async HTTP client wired to the ASGI app."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
