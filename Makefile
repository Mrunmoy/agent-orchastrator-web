SHELL := /bin/bash
ROOT := $(CURDIR)
PYTHON ?= python3
PORT ?= 8080
AGENTS ?=

.PHONY: help serve ui-shot test-ui verify parallel-init parallel-status handoff-packs task-worktree task-prompt task-ready task-shell \
	test test-backend test-frontend lint lint-backend lint-frontend format-check run-backend run-frontend

help:
	@echo "Targets:"
	@echo "  make serve      - serve project files at http://localhost:$(PORT)"
	@echo "  make ui-shot    - capture mock UI screenshot to artifacts/screenshots/"
	@echo "  make test-ui    - run UI smoke test"
	@echo "  make verify     - run core autonomous verification checks"
	@echo "  make parallel-init AGENTS=\"codex-ui claude-orch\" - create per-agent worktrees"
	@echo "  make parallel-status - show worktree and agent branch status"
	@echo "  make handoff-packs - generate codex-code/claude-code kickoff packs"
	@echo "  make task-worktree TASK_ID=UI-001 PREFIX=claude - create worktree by task id"
	@echo "  make task-prompt TASK_ID=SETUP-001 PREFIX=claude WORKER=claude-1 - print worker prompt"
	@echo "  make task-ready TASK_ID=SETUP-001 PREFIX=claude WORKER=claude-1 - create worktree + write TASK_PROMPT.md"
	@echo "  make task-shell TASK_ID=SETUP-001 PREFIX=claude WORKER=claude-1 - create worktree + prompt + enter shell"
	@echo ""
	@echo "Dev commands:"
	@echo "  make test           - run backend + frontend tests"
	@echo "  make test-backend   - run backend tests (pytest)"
	@echo "  make test-frontend  - run frontend tests (vitest)"
	@echo "  make lint           - run backend + frontend linters"
	@echo "  make lint-backend   - run ruff on backend"
	@echo "  make lint-frontend  - run eslint on frontend"
	@echo "  make format-check   - check formatting (black + prettier)"
	@echo "  make run-backend    - start uvicorn dev server"
	@echo "  make run-frontend   - start vite dev server"

# ---------------------------------------------------------------------------
# Dev commands (SETUP-003)
# ---------------------------------------------------------------------------

test: test-backend test-frontend

test-backend:
	cd $(ROOT)/backend && $(PYTHON) -m pytest -q

test-frontend:
	cd $(ROOT)/frontend && npm test

lint: lint-backend lint-frontend

lint-backend:
	cd $(ROOT)/backend && $(PYTHON) -m ruff check src/ tests/

lint-frontend:
	cd $(ROOT)/frontend && npm run lint

format-check:
	cd $(ROOT)/backend && $(PYTHON) -m black --check src/ tests/
	cd $(ROOT)/frontend && npm run format:check

run-backend:
	cd $(ROOT)/backend && $(PYTHON) -m uvicorn agent_orchestrator.api:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd $(ROOT)/frontend && npm run dev

# ---------------------------------------------------------------------------

serve:
	python3 -m http.server $(PORT) --directory $(ROOT)

ui-shot:
	python3 scripts/capture_mock.py --port $(PORT)

test-ui:
	pytest -q tests/ui/test_mockup.py

verify: test-ui ui-shot
	@echo "Verification complete."

parallel-init:
	@if [ -z "$(AGENTS)" ]; then \
		echo "Usage: make parallel-init AGENTS=\"codex-ui claude-orch ollama-data\""; \
		exit 1; \
	fi
	./scripts/parallel_init.sh $(AGENTS)

parallel-status:
	./scripts/parallel_status.sh

handoff-packs:
	./scripts/handoff_prepare.sh

task-worktree:
	@if [ -z "$(TASK_ID)" ]; then \
		echo "Usage: make task-worktree TASK_ID=UI-001 PREFIX=claude"; \
		exit 1; \
	fi
	./scripts/task_worktree.py "$(TASK_ID)" --branch-prefix "$(if $(PREFIX),$(PREFIX),claude)"

task-prompt:
	@if [ -z "$(TASK_ID)" ]; then \
		echo "Usage: make task-prompt TASK_ID=SETUP-001 PREFIX=claude WORKER=claude-1"; \
		exit 1; \
	fi
	./scripts/task_prompt.py "$(TASK_ID)" \
		--prefix "$(if $(PREFIX),$(PREFIX),claude)" \
		--worker-name "$(if $(WORKER),$(WORKER),worker)"

task-ready:
	@if [ -z "$(TASK_ID)" ]; then \
		echo "Usage: make task-ready TASK_ID=SETUP-001 PREFIX=claude WORKER=claude-1"; \
		exit 1; \
	fi
	./scripts/task_prepare.sh "$(TASK_ID)" "$(if $(PREFIX),$(PREFIX),claude)" "$(if $(WORKER),$(WORKER),worker)"

task-shell:
	@if [ -z "$(TASK_ID)" ]; then \
		echo "Usage: make task-shell TASK_ID=SETUP-001 PREFIX=claude WORKER=claude-1"; \
		exit 1; \
	fi
	./scripts/task_prepare.sh "$(TASK_ID)" "$(if $(PREFIX),$(PREFIX),claude)" "$(if $(WORKER),$(WORKER),worker)" --shell
