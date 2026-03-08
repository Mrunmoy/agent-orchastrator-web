"""Shared test fixtures and configuration."""

import os

import pytest

# Force in-memory DB for all tests — must run before config singleton is created.
os.environ["DB_PATH"] = ":memory:"

from agent_orchestrator.config import reset_config
from agent_orchestrator.config_loaders.personalities import _clear_cache as _clear_personalities_cache


@pytest.fixture(autouse=True)
def _reset_singletons():
    yield
    reset_config()
    _clear_personalities_cache()
