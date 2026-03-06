SHELL := /bin/bash
ROOT := $(CURDIR)
PORT ?= 8080

.PHONY: help serve ui-shot test-ui verify

help:
	@echo "Targets:"
	@echo "  make serve      - serve project files at http://localhost:$(PORT)"
	@echo "  make ui-shot    - capture mock UI screenshot to artifacts/screenshots/"
	@echo "  make test-ui    - run UI smoke test"
	@echo "  make verify     - run core autonomous verification checks"

serve:
	python3 -m http.server $(PORT) --directory $(ROOT)

ui-shot:
	python3 scripts/capture_mock.py --port $(PORT)

test-ui:
	pytest -q tests/ui/test_mockup.py

verify: test-ui ui-shot
	@echo "Verification complete."
