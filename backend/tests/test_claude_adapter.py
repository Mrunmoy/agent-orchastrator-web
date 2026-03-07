"""Tests for Claude CLI adapter."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent_orchestrator.adapters.base import AdapterResult, AdapterStatus, BaseAdapter
from agent_orchestrator.adapters.claude_adapter import ClaudeAdapter


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.new_event_loop().run_until_complete(coro)


class TestClaudeAdapterInterface:
    def test_is_subclass_of_base_adapter(self):
        assert issubclass(ClaudeAdapter, BaseAdapter)

    def test_can_instantiate(self):
        adapter = ClaudeAdapter()
        assert adapter is not None


class TestIsAvailable:
    @patch("shutil.which", return_value="/usr/bin/claude")
    def test_available_when_claude_binary_found(self, mock_which):
        adapter = ClaudeAdapter()
        assert adapter.is_available() is True
        mock_which.assert_called_once_with("claude")

    @patch("shutil.which", return_value=None)
    def test_not_available_when_binary_missing(self, mock_which):
        adapter = ClaudeAdapter()
        assert adapter.is_available() is False


class TestSendPrompt:
    def _adapter(self):
        return ClaudeAdapter()

    def test_send_prompt_returns_adapter_result(self):
        adapter = self._adapter()
        mock_result = {
            "result": "Hello, I can help with that.",
            "session_id": "sess-abc123",
        }
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (json.dumps(mock_result), 0)
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp/test"))
        assert isinstance(result, AdapterResult)
        assert result.text == "Hello, I can help with that."
        assert result.session_id == "sess-abc123"
        assert result.status == AdapterStatus.IDLE

    def test_send_prompt_builds_correct_command(self):
        adapter = self._adapter()
        mock_result = {"result": "ok", "session_id": "s1"}
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (json.dumps(mock_result), 0)
            _run(adapter.send_prompt("Fix the bug", working_dir="/home/user/project"))
        cmd = mock_run.call_args[0][0]
        assert "claude" in cmd
        assert "--print" in cmd or "-p" in cmd
        assert "--output-format" in cmd
        assert "json" in cmd

    def test_send_prompt_with_session_id(self):
        adapter = self._adapter()
        mock_result = {"result": "continued", "session_id": "sess-existing"}
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (json.dumps(mock_result), 0)
            _run(
                adapter.send_prompt(
                    "Continue", working_dir="/tmp/test", session_id="sess-existing"
                )
            )
        cmd = mock_run.call_args[0][0]
        assert "--resume" in cmd
        assert "sess-existing" in cmd

    def test_send_prompt_timeout(self):
        adapter = self._adapter()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = TimeoutError()
            result = _run(
                adapter.send_prompt("Hello", working_dir="/tmp/test", timeout_seconds=1.0)
            )
        assert result.status == AdapterStatus.TIMED_OUT
        assert "timed out" in result.text.lower()

    def test_send_prompt_cli_error(self):
        adapter = self._adapter()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("Error: something went wrong", 1)
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp/test"))
        assert result.status == AdapterStatus.ERROR
        assert "something went wrong" in result.text.lower()

    def test_send_prompt_malformed_json(self):
        adapter = self._adapter()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("not valid json {{{", 0)
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp/test"))
        assert result.status == AdapterStatus.ERROR


class TestResumeSession:
    def _adapter(self):
        return ClaudeAdapter()

    def test_resume_session_uses_resume_flag(self):
        adapter = self._adapter()
        mock_result = {"result": "resumed", "session_id": "sess-abc"}
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (json.dumps(mock_result), 0)
            result = _run(
                adapter.resume_session("sess-abc", "Continue work", working_dir="/tmp/test")
            )
        cmd = mock_run.call_args[0][0]
        assert "--resume" in cmd
        assert "sess-abc" in cmd
        assert result.text == "resumed"
        assert result.session_id == "sess-abc"

    def test_resume_session_timeout(self):
        adapter = self._adapter()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = TimeoutError()
            result = _run(
                adapter.resume_session(
                    "sess-abc", "Continue", working_dir="/tmp/test", timeout_seconds=1.0
                )
            )
        assert result.status == AdapterStatus.TIMED_OUT


class TestRunCli:
    def _adapter(self):
        return ClaudeAdapter()

    def test_run_cli_captures_stdout(self):
        adapter = self._adapter()
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"output text", b"")
        mock_proc.returncode = 0
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            stdout, code = _run(
                adapter._run_cli(
                    ["claude", "-p", "hello"], working_dir="/tmp", timeout_seconds=30.0
                )
            )
        assert stdout == "output text"
        assert code == 0

    def test_run_cli_timeout_kills_process(self):
        adapter = self._adapter()
        mock_proc = AsyncMock()
        mock_proc.communicate.side_effect = asyncio.TimeoutError()
        mock_proc.kill = MagicMock()
        mock_proc.wait = AsyncMock()
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            with pytest.raises(asyncio.TimeoutError):
                _run(
                    adapter._run_cli(
                        ["claude", "-p", "hello"], working_dir="/tmp", timeout_seconds=0.1
                    )
                )
        mock_proc.kill.assert_called_once()
