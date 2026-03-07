# Playbook: API-001 FastAPI App + Health Endpoint

## What was built

- FastAPI application instance exported as `agent_orchestrator.api:app`
- `GET /health` endpoint returning `{"ok": true, "data": {"status": "healthy"}}`
- `GET /state` endpoint returning `{"ok": true, "data": {"version": "0.1.0", "status": "idle"}}`
- All responses use the standard `ok` envelope convention

## How to run

```bash
nix develop
cd backend
uvicorn agent_orchestrator.api:app --reload
```

Then test:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/state
```

## How to test

```bash
nix develop
cd backend
python -m pytest tests/test_api_health.py -q
```

## Key files

| File | Purpose |
|------|---------|
| `backend/src/agent_orchestrator/api/__init__.py` | App factory (`create_app()`) and module-level `app` |
| `backend/src/agent_orchestrator/api/routes/health.py` | Health and state route handlers + `ok_response` helper |
| `backend/tests/test_api_health.py` | 9 tests covering both endpoints |

## Design decisions

- **App factory pattern**: `create_app()` allows test isolation and future configuration.
- **`ok_response` helper**: Centralises envelope construction; error envelope helper deferred.
- **Synchronous endpoints**: Health/state are trivial; no async needed.
- **Version hardcoded**: Matches `pyproject.toml` 0.1.0. Will be read dynamically when
  `importlib.metadata` integration is added.

## Nix change

Added `python312Packages.httpx` to `flake.nix` -- required by `fastapi.testclient.TestClient`.
