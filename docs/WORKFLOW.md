# Development Workflow Contract

## Mandatory Steps (every feature/slice)

For every feature/slice, follow these steps **in order**:

1. **Design doc** — Create `docs/design/2026-MM-DD-<task-id>-<slug>.html` using the gold theme from existing design HTML files. Follow the structure in `docs/templates/feature-design-template.md` but output as HTML.
2. **Failing tests first** — Write unit tests before implementation. Tests must fail initially (TDD).
3. **Implement** — Small, focused commits. Run `make lint` and `make format-check` before considering done.
4. **Verify** — Run `make test` to confirm all tests pass (not just yours — the full suite).
5. **Playbook** — Create `docs/playbook/2026-MM-DD-<task-id>-<slug>.html` using the teal theme. Document gotchas, debug findings, how-to-run, key files.
6. **Saga** — Create `docs/saga/2026-MM-DD-chapter-<narrative-title>.html` using the rose theme. Write in **narrative/storytelling style** (like a D&D campaign log). Technical details belong in design/playbook, not here.
7. **Update indexes** — Add links to your new HTML files in `docs/design/index.html`, `docs/playbook/index.html`, and `docs/saga/index.html`.
8. **Update decisions/changelog** where applicable.

## Doc Format Rules

- **All design, playbook, and saga docs MUST be HTML** — not markdown.
- Match the existing themed styles (gold for design, teal for playbook, rose for saga).
- See existing HTML files in each directory for the exact CSS to copy.
- Saga chapters use **narrative voice** — tell the story of what happened as if recounting a quest, not writing a technical report.

## Tracking File Updates (after merge)

Three files **must stay in sync** after any task status change:
1. `TASKS.md` — Mark task checkbox `[x]`, update "Current State Snapshot"
2. `docs/coordination/task-board.md` — Update status to `Done`, set owner, set branch
3. `config/tasks.json` — Update `"status"` field to `"Done"`

## Environment

- Always work inside `nix develop` shell.
- Backend: `cd backend && python -m pytest -q` for tests, `ruff check src/ tests/` for lint.
- Frontend: `cd frontend && npm test` for tests, `npm run lint` for lint.
- Full suite: `make test`, `make lint`, `make format-check` from repo root.

## Slice Checklist (use as final verification)

See `docs/checklists/slice-checklist.md` for the complete checklist.
