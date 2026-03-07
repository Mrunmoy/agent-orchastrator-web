"""Tests for Codex CLI adapter."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent_orchestrator.adapters.base import AdapterResult, AdapterStatus, BaseAdapter
from agent_orchestrator.adapters.codex_adapter import CodexAdapter


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.new_event_loop().run_until_complete(coro)


class TestCodexAdapterInterface:
    def test_is_subclass_of_base_adapter(self):
        assert issubclass(CodexAdapter, BaseAdapter)

    def test_can_instantiate(self):
        adapter = CodexAdapter()
        assert adapter is not None


class TestIsAvailable:
    @patch("shutil.which", return_value="/usr/bin/codex")
    def test_available_when_codex_binary_found(self, mock_which):
        adapter = CodexAdapter()
        assert adapter.is_available() is True
        mock_which.assert_called_once_with("codex")

    @patch("shutil.which", return_value=None)
    def test_not_available_when_binary_missing(self, mock_which):
        adapter = CodexAdapter()
        assert adapter.is_available() is False


class TestSendPrompt:
    def _adapter(self):
        return CodexAdapter()

    def test_send_prompt_returns_adapter_result(self):
        adapter = self._adapter()
        mock_output = json.dumps({
            "id": "resp-abc123",
            "output": [
                {"type": "message", "role": "assistant", "content": [
                    {"type": "output_text", "text": "Hello, I can help with that."}
                ]}
            ],
        })
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (mock_output, 0)
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp/test"))
        assert isinstance(result, AdapterResult)
        assert result.text == "Hello, I can help with that."
        assert result.session_id == "resp-abc123"
        assert result.status == AdapterStatus.IDLE

    def test_send_prompt_builds_correct_command(self):
        adapter = self._adapter()
        mock_output = json.dumps({
            "id": "resp-1",
            "output": [
                {"type": "message", "role": "assistant", "content": [
                    {"type": "output_text", "text": "ok"}
                ]}
            ],
        })
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (mock_output, 0)
            _run(adapter.send_prompt("Fix the bug", working_dir="/home/user/project"))
        cmd = mock_run.call_args[0][0]
        assert "codex" in cmd
        assert "--json" in cmd or "-j" in cmd
        assert "Fix the bug" in cmd

    def test_send_prompt_with_session_id(self):
        adapter = self._adapter()
        mock_output = json.dumps({
            "id": "resp-existing",
            "output": [
                {"type": "message", "role": "assistant", "content": [
                    {"type": "output_text", "text": "continued"}
                ]}
            ],
        })
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (mock_output, 0)
            _run(
                adapter.send_prompt(
                    "Continue", working_dir="/tmp/test", session_id="sess-existing"
                )
            )
        cmd = mock_run.call_args[0][0]
        assert "--session" in cmd
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

    def test_send_prompt_extracts_multiple_output_texts(self):
        adapter = self._adapter()
        mock_output = json.dumps({
            "id": "resp-multi",
            "output": [
                {"type": "message", "role": "assistant", "content": [
                    {"type": "output_text", "text": "Part one."},
                    {"type": "output_text", "text": " Part two."},
                ]},
            ],
        })
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (mock_output, 0)
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp/test"))
        assert result.text == "Part one. Part two."

    def test_send_prompt_no_output_messages(self):
        adapter = self._adapter()
        mock_output = json.dumps({"id": "resp-empty", "output": []})
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (mock_output, 0)
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp/test"))
        assert result.text == ""
        assert result.status == AdapterStatus.IDLE


class TestResumeSession:
    def _adapter(self):
        return CodexAdapter()

    def test_resume_session_uses_session_flag(self):
        adapter = self._adapter()
        mock_output = json.dumps({
            "id": "resp-abc",
            "output": [
                {"type": "message", "role": "assistant", "content": [
                    {"type": "output_text", "text": "resumed"}
                ]}
            ],
        })
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (mock_output, 0)
            result = _run(
                adapter.resume_session("sess-abc", "Continue work", working_dir="/tmp/test")
            )
        cmd = mock_run.call_args[0][0]
        assert "--session" in cmd
        assert "sess-abc" in cmd
        assert result.text == "resumed"

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
        return CodexAdapter()

    def test_run_cli_captures_stdout(self):
        adapter = self._adapter()
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"output text", b"")
        mock_proc.returncode = 0
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            stdout, code = _run(
                adapter._run_cli(
                    ["codex", "--json", "hello"], working_dir="/tmp", timeout_seconds=30.0
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
                        ["codex", "--json", "hello"], working_dir="/tmp", timeout_seconds=0.1
                    )
                )
        mock_proc.kill.assert_called_once()
