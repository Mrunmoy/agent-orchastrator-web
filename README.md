# Agent Orchestrator Web

LAN-accessible, CLI-native multi-agent orchestration workspace.

## Toolchain
This project uses **Nix** for reproducible development.

```bash
nix develop
```

Optional:
```bash
direnv allow
```

## Dev Commands
```bash
make serve
make test-ui
make ui-shot
make verify
```

## Documentation
- `TASKS.md` - task tracker
- `docs/DESIGN.md` - high-level design
- `docs/IMPLEMENTATION_PLAN_V1.md` - sprint implementation plan
- `docs/DEV_ENV.md` - environment and autonomous test loop
- `docs/specs/` - section-by-section implementation contracts
