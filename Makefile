SHELL := /bin/bash
ROOT := $(CURDIR)
PORT ?= 8080
AGENTS ?=

.PHONY: help serve ui-shot test-ui verify parallel-init parallel-status handoff-packs

help:
	@echo "Targets:"
	@echo "  make serve      - serve project files at http://localhost:$(PORT)"
	@echo "  make ui-shot    - capture mock UI screenshot to artifacts/screenshots/"
	@echo "  make test-ui    - run UI smoke test"
	@echo "  make verify     - run core autonomous verification checks"
	@echo "  make parallel-init AGENTS=\"codex-ui claude-orch\" - create per-agent worktrees"
	@echo "  make parallel-status - show worktree and agent branch status"
	@echo "  make handoff-packs - generate codex-code/claude-code kickoff packs"

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
