# Playbook: DATA-002 Migration/Bootstrap Loader

## What it does

`DatabaseManager` bootstraps a SQLite database from `schema.sql` and provides
connection management with foreign keys enabled and WAL mode on file-backed DBs.

## Quick start

```python
from agent_orchestrator.storage import DatabaseManager

# File-backed database
db = DatabaseManager("data/orchestrator.db")
db.initialize()

# Use the connection
with db.connection() as conn:
    conn.execute("INSERT INTO agent ...")
    conn.commit()

# Check schema version
print(db.schema_version)  # 1

# Cleanup
db.close()
```

## In-memory (for tests)

```python
db = DatabaseManager(":memory:")
db.initialize()
```

## Key behaviours

- **Idempotent**: `initialize()` can be called multiple times safely.
- **WAL mode**: Automatically enabled on file-backed databases via `schema.sql`.
- **Foreign keys**: Enabled on every connection.
- **Schema version**: Tracked via `PRAGMA user_version` (currently `1`).

## Files

- Implementation: `backend/src/agent_orchestrator/storage/db.py`
- Schema DDL: `backend/src/agent_orchestrator/storage/schema.sql`
- Tests: `backend/tests/test_db_manager.py`
- Design doc: `docs/design/data-002-migration-loader.md`
