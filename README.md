# Agent Orchestrator Web

[![CI](https://github.com/Mrunmoy/agent-orchastrator-web/actions/workflows/ci.yml/badge.svg)](https://github.com/Mrunmoy/agent-orchastrator-web/actions/workflows/ci.yml)
[![Status: WIP](https://img.shields.io/badge/status-work%20in%20progress-orange)](#)

A local-first, LAN-accessible orchestration cockpit for running multiple CLI AI agents (Claude, Codex, Ollama) in structured workflows. Instead of chatting with one model at a time, you set up multi-agent conversations where agents debate, agree, and build software together through phased execution.

**What it lets you do:**

- Run parallel AI agents that discuss design decisions before writing code
- Execute structured workflows: design debate, TDD planning, implementation, integration, docs, merge
- Batch-execute agent turns (20 at a time) with pause points for human steering
- Resume conversations from checkpoints instead of replaying full transcripts
- Monitor agent agreement/disagreement in real time via a Slack-like UI

## Quick Start

### Prerequisites

- [Nix](https://nixos.org/download/) package manager
- Git

### Clone and Setup

```bash
git clone git@github.com:Mrunmoy/agent-orchastrator-web.git
cd agent-orchastrator-web
nix develop
```

That's it. The Nix dev shell provides Python 3.12, Node.js 22, and all tooling. Frontend dependencies install automatically on shell entry.

If you use [direnv](https://direnv.net/), you can skip typing `nix develop` every time:

```bash
direnv allow
```

### Verify Everything Works

```bash
make test-all    # run backend + frontend tests
make verify      # UI smoke test + screenshot
```

### Start the Full Stack (Single Command)

```bash
make dev-up
```

This starts both backend and frontend in the background.

Useful commands:

```bash
make dev-status   # show PIDs + URLs
make dev-logs     # show recent backend/frontend logs
make dev-down     # stop both services
```

### Start for LAN Access (Phone/Tablet/Laptop)

```bash
make dev-up-lan
```

This binds services to `0.0.0.0` and prints LAN URLs.

## API Quick Tour

The backend exposes a REST API. All responses use a standard envelope:

```json
{"ok": true, "data": { ... }}
```

Example — list conversations:

```bash
curl http://localhost:8000/api/conversations
```

Example — create a conversation:

```bash
curl -X POST http://localhost:8000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "Design debate: auth module"}'
```

## Project Structure

```
backend/          Python (FastAPI) — API, adapters, orchestrator, storage
frontend/         TypeScript + React 19 — Vite, Vitest, Testing Library
config/           Task registry, agent personality profiles
docs/             Design docs, specs, coordination, ADRs, playbooks
```

## Current Status

This project is under active development. The backend API, adapter layer, orchestration engine, and frontend shell are functional. The UI is being built out incrementally. See [TASKS.md](./TASKS.md) for the full backlog.

## License

Licensed under the [Mrunmoy + Claude + Codex Appreciation License v1.0](./LICENSE).
Usage requires a visible acknowledgment thanking **Mrunmoy**, **Claude**, and **Codex**.
