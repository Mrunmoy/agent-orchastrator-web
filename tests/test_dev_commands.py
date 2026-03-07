"""Tests for SETUP-003: shared dev commands in root Makefile."""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_make(target: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["make", "-n", target],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _make_has_target(target: str) -> bool:
    """Check that a Makefile target exists (dry-run succeeds)."""
    result = _run_make(target)
    return result.returncode == 0


def test_make_test_target_exists():
    assert _make_has_target("test"), "make test target should exist"


def test_make_test_backend_target_exists():
    assert _make_has_target("test-backend"), "make test-backend target should exist"


def test_make_test_frontend_target_exists():
    assert _make_has_target("test-frontend"), "make test-frontend target should exist"


def test_make_lint_target_exists():
    assert _make_has_target("lint"), "make lint target should exist"


def test_make_lint_backend_target_exists():
    assert _make_has_target("lint-backend"), "make lint-backend target should exist"


def test_make_lint_frontend_target_exists():
    assert _make_has_target("lint-frontend"), "make lint-frontend target should exist"


def test_make_format_check_target_exists():
    assert _make_has_target("format-check"), "make format-check target should exist"


def test_make_run_backend_target_exists():
    assert _make_has_target("run-backend"), "make run-backend target should exist"


def test_make_run_frontend_target_exists():
    assert _make_has_target("run-frontend"), "make run-frontend target should exist"


def test_make_dev_up_target_exists():
    assert _make_has_target("dev-up"), "make dev-up target should exist"


def test_make_dev_down_target_exists():
    assert _make_has_target("dev-down"), "make dev-down target should exist"


def test_make_dev_status_target_exists():
    assert _make_has_target("dev-status"), "make dev-status target should exist"


def test_make_test_wires_backend_and_frontend_commands():
    result = _run_make("test")
    assert result.returncode == 0, f"make -n test failed:\n{result.stdout}\n{result.stderr}"
    assert "pytest -q" in result.stdout
    assert "npm test" in result.stdout


def test_make_lint_wires_backend_and_frontend_commands():
    result = _run_make("lint")
    assert result.returncode == 0, f"make -n lint failed:\n{result.stdout}\n{result.stderr}"
    assert "ruff check src/ tests/" in result.stdout
    assert "npm run lint" in result.stdout


def test_make_format_check_wires_backend_and_frontend_commands():
    result = _run_make("format-check")
    assert (
        result.returncode == 0
    ), f"make -n format-check failed:\n{result.stdout}\n{result.stderr}"
    assert "black --check src/ tests/" in result.stdout
    assert "npm run format:check" in result.stdout


def test_make_dev_up_wires_stack_start_script():
    result = _run_make("dev-up")
    assert result.returncode == 0, f"make -n dev-up failed:\n{result.stdout}\n{result.stderr}"
    assert "./scripts/dev_stack.sh start" in result.stdout


def test_make_dev_down_wires_stack_stop_script():
    result = _run_make("dev-down")
    assert (
        result.returncode == 0
    ), f"make -n dev-down failed:\n{result.stdout}\n{result.stderr}"
    assert "./scripts/dev_stack.sh stop" in result.stdout


def test_make_dev_status_wires_stack_status_script():
    result = _run_make("dev-status")
    assert (
        result.returncode == 0
    ), f"make -n dev-status failed:\n{result.stdout}\n{result.stderr}"
    assert "./scripts/dev_stack.sh status" in result.stdout
