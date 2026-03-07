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
