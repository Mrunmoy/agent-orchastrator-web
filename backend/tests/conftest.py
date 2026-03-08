"""Shared test fixtures and configuration."""

import os

# Force in-memory DB for all tests — must run before config singleton is created.
os.environ["DB_PATH"] = ":memory:"
