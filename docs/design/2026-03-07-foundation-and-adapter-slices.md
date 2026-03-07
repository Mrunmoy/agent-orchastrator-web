# 2026-03-07 Foundation And Adapter Slices

## Context
Completed initial parallel slices:
- SETUP-001 backend Python package layout
- SETUP-002 frontend TypeScript shell
- ADPT-001 Claude CLI adapter baseline

## Decisions
- Backend package follows `src/` layout with strict module boundaries (`adapters`, `api`, `orchestrator`, `runtime`, `storage`).
- Frontend shell uses React + Vite + TypeScript for fast iteration and testable component surface.
- Claude adapter returns normalized `AdapterResult` and supports resume semantics via session ID.

## Rationale
- `src/` layout avoids import path ambiguity and scales cleanly as backend modules grow.
- Vite + Vitest gives lightweight developer loop for UI-first iteration.
- A shared adapter interface enables plugging Codex/Ollama adapters later without orchestrator coupling.

## Follow-up
- Implement Codex adapter (`ADPT-002`) with parity behaviors.
- Add stderr-aware error reporting and richer adapter metadata.
- Add FastAPI skeleton (`API-001`) against the new backend layout.
