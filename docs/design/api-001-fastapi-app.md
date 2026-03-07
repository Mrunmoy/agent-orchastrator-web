# API-001: FastAPI App + Health Endpoint

## Context

The backend package structure exists (`backend/src/agent_orchestrator/api/`) but contains
no application instance or routes. We need a runnable FastAPI app with a health endpoint
so downstream tasks (WebSocket layer, orchestrator API, frontend integration) have a
working HTTP server to build on.

## Requirements

1. A FastAPI `app` instance importable as `agent_orchestrator.api:app`.
2. `GET /health` returns `{"ok": true, "data": {"status": "healthy"}}`.
3. `GET /state` returns `{"ok": true, "data": {"version": "0.1.0", "status": "idle"}}`.
4. All responses follow the `{"ok": true/false, ...}` envelope convention (spec 10).
5. The app is launchable via `uvicorn agent_orchestrator.api:app`.

## Proposed Design

### Module layout

```
backend/src/agent_orchestrator/api/
    __init__.py          # creates FastAPI app, includes routers, exports `app`
    routes/
        __init__.py      # (unchanged)
        health.py        # GET /health, GET /state
```

### Response envelope

A small helper function `ok_response(data)` produces the standard envelope.
Error envelope helper deferred to a later task (error-handling middleware).

### Routes

- **GET /health** -- Liveness/readiness probe. Returns status "healthy".
- **GET /state**  -- App metadata stub. Returns version from package metadata and
  a hardcoded "idle" status (will be wired to orchestrator state later).

### App creation

`create_app()` factory in `api/__init__.py` builds the FastAPI instance and includes
the health router. Module-level `app = create_app()` enables `uvicorn` import.

## Alternatives Considered

- Putting the app in a separate `backend/src/agent_orchestrator/main.py` file.
  Rejected: the task spec says to export from `api/__init__.py`, and keeping
  the app next to the routes package is conventional for small FastAPI projects.

## Test Strategy

- Use `fastapi.testclient.TestClient` (synchronous, simpler than httpx async for
  these basic endpoints).
- Tests in `backend/tests/test_api_health.py`.
- Verify response status codes, JSON structure, and envelope fields.

## Acceptance Criteria

- [ ] `pytest -q` passes with health and state endpoint tests.
- [ ] `ruff check` and `black --check` pass.
- [ ] `uvicorn agent_orchestrator.api:app` starts without error.
- [ ] `GET /health` returns 200 with correct envelope.
- [ ] `GET /state` returns 200 with version and status.
