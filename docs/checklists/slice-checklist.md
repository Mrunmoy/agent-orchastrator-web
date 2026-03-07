# Slice Checklist

Use this checklist to verify every task is fully complete before marking Done.

## Implementation
- [ ] Design doc created as **HTML** in `docs/design/` (gold theme)
- [ ] Unit tests written **before** implementation (TDD)
- [ ] Implementation completed in small commits
- [ ] `make test` passes (full suite, not just your tests)
- [ ] `make lint` passes
- [ ] `make format-check` passes

## Documentation (all HTML, not markdown)
- [ ] Playbook entry created as **HTML** in `docs/playbook/` (teal theme)
- [ ] Saga chapter created as **HTML** in `docs/saga/` (rose theme, narrative voice)
- [ ] `docs/design/index.html` updated with link to new design doc
- [ ] `docs/playbook/index.html` updated with link to new playbook entry
- [ ] `docs/saga/index.html` updated with link to new saga chapter
- [ ] Changelog entry added (if user-facing)

## Tracking (updated after merge by coordinator)
- [ ] `TASKS.md` — checkbox marked `[x]`, "Current State Snapshot" updated
- [ ] `docs/coordination/task-board.md` — status set to `Done`, owner and branch filled
- [ ] `config/tasks.json` — status field set to `"Done"`
