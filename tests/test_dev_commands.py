"""Tests for SETUP-003: shared dev commands in root Makefile."""

import subprocess

ROOT = "/home/mrumoy/sandbox/agent-orchestrator-web"


def _run_make(target: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["make", "-n", target],
        cwd=ROOT,
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


def test_make_test_runs_successfully():
    """Actually run make test and verify exit 0."""
    result = subprocess.run(
        ["make", "test"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"make test failed:\n{result.stdout}\n{result.stderr}"


def test_make_lint_runs_successfully():
    """Actually run make lint and verify exit 0."""
    result = subprocess.run(
        ["make", "lint"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"make lint failed:\n{result.stdout}\n{result.stderr}"


def test_make_format_check_runs_successfully():
    """Actually run make format-check and verify exit 0."""
    result = subprocess.run(
        ["make", "format-check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"make format-check failed:\n{result.stdout}\n{result.stderr}"
