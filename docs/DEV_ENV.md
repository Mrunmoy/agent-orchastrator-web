# Development Environment

## Choice
This project uses **Nix** as the primary dev environment (not Docker).

## Why Nix
1. Fast local iteration for autonomous agents without container rebuild cycles.
2. Reproducible toolchain pinned in `flake.nix`.
3. Works naturally with local CLI agents (`codex`, `claude`, `ollama`) and host file access.
4. Easier UI screenshot/testing loop during development.

## Enter Environment
```bash
cd <repo-root>
nix develop
```

## Autonomous UI Workflow
```bash
make serve      # run local static server
make test-ui    # run Playwright smoke test
make ui-shot    # capture screenshot artifact
make verify     # run core automated checks
```

Screenshots are stored in:
- `artifacts/screenshots/mockup-test.png`
- `artifacts/screenshots/mockup-latest.png`
