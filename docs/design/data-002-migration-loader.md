# Feature Design: DATA-002 Migration/Bootstrap Loader

## Context
- Problem: The storage module has a `schema.sql` DDL file but no programmatic way to initialize a database, manage connections, or track schema versions. Application code has no entry point for bootstrapping the database.
- Scope: `backend/src/agent_orchestrator/storage/db.py` -- a `DatabaseManager` class that reads and applies `schema.sql`, provides connection management, and tracks schema version.
- Non-goals: Full migration framework, rollback support, multi-file migration chains, connection pooling.

## Requirements
- Functional:
  - `DatabaseManager(db_path)` accepts a file path or `:memory:`.
  - `initialize()` reads `schema.sql` and executes it, sets WAL mode on file-backed DBs, and records schema version via `PRAGMA user_version`.
  - `initialize()` is idempotent -- safe to call multiple times.
  - `connection()` context manager yields an `sqlite3.Connection` with foreign keys enabled.
  - `close()` closes the underlying connection.
  - Schema version is tracked using SQLite's `PRAGMA user_version` (currently version 1).
- Non-functional:
  - Thread safety is not required (single-writer SQLite model).
  - No external dependencies beyond Python stdlib.

## Proposed Design
- Single file: `backend/src/agent_orchestrator/storage/db.py`.
- `DatabaseManager` holds a single `sqlite3.Connection` internally.
- `initialize()`:
  1. Reads `schema.sql` from the same package directory.
  2. Executes the DDL via `executescript()`.
  3. Sets `PRAGMA user_version = 1` if not already set.
- `connection()` is a `@contextmanager` that yields the internal connection. The caller is responsible for committing; the context manager handles nothing beyond yielding.
- `close()` calls `conn.close()`.
- `schema_version` property reads `PRAGMA user_version` and returns the integer.
- Re-export `DatabaseManager` from `storage/__init__.py`.

## Alternatives Considered
1. `schema_version` table -- adds complexity; `PRAGMA user_version` is simpler and built into SQLite.
2. Alembic or similar migration tool -- overkill for a single-schema local-first app at this stage.
3. Connection-per-call model -- unnecessary overhead; single persistent connection matches SQLite's single-writer design.

## Test Strategy
- Tests in `backend/tests/test_db_manager.py` (written before implementation).
- Test cases:
  - `DatabaseManager` creates and initializes an in-memory DB.
  - All 8 expected tables exist after `initialize()`.
  - `schema_version` returns 1 after initialization.
  - `initialize()` is idempotent (calling twice does not raise).
  - `connection()` context manager yields a working connection.
  - WAL mode is active on file-backed databases.
  - `close()` closes the connection.
  - Foreign keys are enabled on connections.

## File Changes
- New: `backend/src/agent_orchestrator/storage/db.py`
- Modified: `backend/src/agent_orchestrator/storage/__init__.py` (re-export)
- New: `backend/tests/test_db_manager.py`
- New: `docs/design/data-002-migration-loader.md` (this file)
- New: `docs/playbook/data-002-migration-loader.md`
