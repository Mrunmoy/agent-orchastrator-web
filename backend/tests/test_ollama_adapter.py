"""Tests for Ollama memo adapter."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from agent_orchestrator.adapters.base import AdapterResult, AdapterStatus


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.new_event_loop().run_until_complete(coro)


class TestOllamaAdapterConfig:
    def test_default_model(self):
        from agent_orchestrator.adapters.ollama_adapter import OllamaAdapterConfig

        config = OllamaAdapterConfig()
        assert config.model == "llama3.2"

    def test_default_host(self):
        from agent_orchestrator.adapters.ollama_adapter import OllamaAdapterConfig

        config = OllamaAdapterConfig()
        assert config.host == "http://localhost:11434"

    def test_default_timeout(self):
        from agent_orchestrator.adapters.ollama_adapter import OllamaAdapterConfig

        config = OllamaAdapterConfig()
        assert config.timeout_seconds == 120

    def test_custom_config_overrides(self):
        from agent_orchestrator.adapters.ollama_adapter import OllamaAdapterConfig

        config = OllamaAdapterConfig(
            model="mistral", host="http://remote:11434", timeout_seconds=60
        )
        assert config.model == "mistral"
        assert config.host == "http://remote:11434"
        assert config.timeout_seconds == 60


class TestRun:
    def test_successful_run_returns_adapter_result(self):
        from agent_orchestrator.adapters.ollama_adapter import run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"This is the memo output.", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(run("Summarize the debate"))

        assert isinstance(result, AdapterResult)
        assert result.text == "This is the memo output."
        assert result.status == AdapterStatus.IDLE

    def test_session_id_is_always_none(self):
        from agent_orchestrator.adapters.ollama_adapter import run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"output", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(run("Summarize"))

        assert result.session_id is None

    def test_timeout_produces_error_result(self):
        from agent_orchestrator.adapters.ollama_adapter import OllamaAdapterConfig, run

        mock_proc = AsyncMock()
        mock_proc.communicate.side_effect = TimeoutError()
        mock_proc.kill = MagicMock()
        mock_proc.wait = AsyncMock()

        config = OllamaAdapterConfig(timeout_seconds=1)
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(run("Summarize", config=config))

        assert result.status == AdapterStatus.TIMED_OUT
        assert "timed out" in result.text.lower()
        assert result.session_id is None

    def test_nonzero_exit_code_captured(self):
        from agent_orchestrator.adapters.ollama_adapter import run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"Error: model not found")
        mock_proc.returncode = 1

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(run("Summarize"))

        assert result.status == AdapterStatus.ERROR
        assert result.session_id is None

    def test_stderr_captured_in_error_field(self):
        from agent_orchestrator.adapters.ollama_adapter import run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"connection refused")
        mock_proc.returncode = 1

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(run("Summarize"))

        assert result.status == AdapterStatus.ERROR
        assert "connection refused" in result.metadata.get("stderr", "")

    def test_prompt_sent_via_stdin(self):
        from agent_orchestrator.adapters.ollama_adapter import run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"response", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            _run(run("Analyze this debate"))

        # Verify stdin=PIPE was used
        call_kwargs = mock_exec.call_args
        assert call_kwargs.kwargs.get("stdin") == asyncio.subprocess.PIPE

        # Verify prompt was sent via communicate (as keyword arg 'input')
        mock_proc.communicate.assert_called_once()
        call_args = mock_proc.communicate.call_args
        assert call_args.kwargs.get("input") == b"Analyze this debate"

    def test_custom_model_used_in_command(self):
        from agent_orchestrator.adapters.ollama_adapter import OllamaAdapterConfig, run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"response", b"")
        mock_proc.returncode = 0

        config = OllamaAdapterConfig(model="mistral")
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            _run(run("Summarize", config=config))

        cmd_args = mock_exec.call_args[0]
        assert "mistral" in cmd_args

    def test_host_passed_via_env(self):
        from agent_orchestrator.adapters.ollama_adapter import OllamaAdapterConfig, run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"response", b"")
        mock_proc.returncode = 0

        config = OllamaAdapterConfig(host="http://remote:11434")
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            _run(run("Summarize", config=config))

        env = mock_exec.call_args.kwargs.get("env", {})
        assert env.get("OLLAMA_HOST") == "http://remote:11434"


class TestCheckAvailable:
    def test_returns_true_when_ollama_list_succeeds(self):
        from agent_orchestrator.adapters.ollama_adapter import check_available

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"NAME\nllama3.2:latest", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(check_available())

        assert result is True

    def test_returns_false_when_ollama_list_fails(self):
        from agent_orchestrator.adapters.ollama_adapter import check_available

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"command not found")
        mock_proc.returncode = 127

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(check_available())

        assert result is False

    def test_returns_false_on_exception(self):
        from agent_orchestrator.adapters.ollama_adapter import check_available

        with patch(
            "asyncio.create_subprocess_exec", side_effect=FileNotFoundError("ollama not found")
        ):
            result = _run(check_available())

        assert result is False
