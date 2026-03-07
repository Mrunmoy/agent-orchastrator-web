"""Contract tests verifying all adapters conform to the BaseAdapter interface.

TEST-002: Adapter contract tests with mocked CLI responses.

These tests ensure that:
1. Each concrete adapter is a subclass of BaseAdapter (where applicable).
2. send_prompt / resume_session return AdapterResult with valid AdapterStatus.
3. Timeout, error, and empty-prompt edge cases are handled uniformly.
4. The normalize module integrates correctly with AdapterResult from every adapter.
"""

from __future__ import annotations

import asyncio
import inspect
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent_orchestrator.adapters.base import AdapterResult, AdapterStatus, BaseAdapter
from agent_orchestrator.adapters.claude_adapter import ClaudeAdapter
from agent_orchestrator.adapters.codex_adapter import CodexAdapter
from agent_orchestrator.adapters.normalize import NormalizedMessage, normalize, normalize_batch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.new_event_loop().run_until_complete(coro)


def _claude_success_json(text: str = "Hello", session_id: str = "sess-1") -> str:
    return json.dumps({"result": text, "session_id": session_id})


def _codex_success_json(text: str = "Hello", resp_id: str = "resp-1") -> str:
    return json.dumps(
        {
            "id": resp_id,
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": text}],
                }
            ],
        }
    )


# Pairs of (AdapterClass, mock_success_output_factory)
CLASS_ADAPTERS = [
    (ClaudeAdapter, _claude_success_json),
    (CodexAdapter, _codex_success_json),
]


# ===================================================================
# 1. Subclass and interface conformance
# ===================================================================


class TestSubclassConformance:
    """Every class-based adapter must be a proper subclass of BaseAdapter."""

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_is_subclass_of_base_adapter(self, cls, _):
        assert issubclass(cls, BaseAdapter)

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_can_instantiate(self, cls, _):
        adapter = cls()
        assert adapter is not None

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_has_send_prompt_method(self, cls, _):
        assert hasattr(cls, "send_prompt")
        assert asyncio.iscoroutinefunction(cls.send_prompt)

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_has_resume_session_method(self, cls, _):
        assert hasattr(cls, "resume_session")
        assert asyncio.iscoroutinefunction(cls.resume_session)

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_has_is_available_method(self, cls, _):
        assert hasattr(cls, "is_available")
        assert callable(cls.is_available)

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_send_prompt_signature_matches_base(self, cls, _):
        base_sig = inspect.signature(BaseAdapter.send_prompt)
        impl_sig = inspect.signature(cls.send_prompt)
        base_params = set(base_sig.parameters.keys())
        impl_params = set(impl_sig.parameters.keys())
        assert base_params == impl_params, (
            f"{cls.__name__}.send_prompt params {impl_params} "
            f"differ from BaseAdapter {base_params}"
        )

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_resume_session_signature_matches_base(self, cls, _):
        base_sig = inspect.signature(BaseAdapter.resume_session)
        impl_sig = inspect.signature(cls.resume_session)
        base_params = set(base_sig.parameters.keys())
        impl_params = set(impl_sig.parameters.keys())
        assert base_params == impl_params


# ===================================================================
# 2. send_prompt contract tests with mocked CLI
# ===================================================================


class TestSendPromptContract:
    """send_prompt must return AdapterResult with correct status for all adapters."""

    @pytest.mark.parametrize("cls,factory", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_successful_response_returns_idle(self, cls, factory):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (factory("response text"), 0)
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp"))
        assert isinstance(result, AdapterResult)
        assert result.status == AdapterStatus.IDLE
        assert "response text" in result.text

    @pytest.mark.parametrize("cls,factory", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_text_field_is_string(self, cls, factory):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (factory("test content"), 0)
            result = _run(adapter.send_prompt("Hi", working_dir="/tmp"))
        assert isinstance(result.text, str)

    @pytest.mark.parametrize("cls,factory", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_status_is_adapter_status_enum(self, cls, factory):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (factory(), 0)
            result = _run(adapter.send_prompt("Hi", working_dir="/tmp"))
        assert isinstance(result.status, AdapterStatus)

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_timeout_returns_timed_out_status(self, cls, _):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = TimeoutError()
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp", timeout_seconds=0.5))
        assert result.status == AdapterStatus.TIMED_OUT
        assert "timed out" in result.text.lower()

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_cli_error_returns_error_status(self, cls, _):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("Error: failure", 1)
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp"))
        assert result.status == AdapterStatus.ERROR

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_malformed_output_returns_error(self, cls, _):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("{{{not json", 0)
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp"))
        assert result.status == AdapterStatus.ERROR

    @pytest.mark.parametrize("cls,factory", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_session_id_is_populated_on_success(self, cls, factory):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (
                factory("ok", "sid-42" if cls is ClaudeAdapter else "sid-42"),
                0,
            )
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp"))
        assert result.session_id is not None

    @pytest.mark.parametrize("cls,factory", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_metadata_is_dict(self, cls, factory):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (factory(), 0)
            result = _run(adapter.send_prompt("Hi", working_dir="/tmp"))
        assert isinstance(result.metadata, dict)

    @pytest.mark.parametrize("cls,factory", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_timeout_parameter_is_accepted(self, cls, factory):
        """Adapters must accept timeout_seconds as keyword arg without error."""
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (factory(), 0)
            result = _run(adapter.send_prompt("Hello", working_dir="/tmp", timeout_seconds=30.0))
        assert isinstance(result, AdapterResult)


# ===================================================================
# 3. resume_session contract tests
# ===================================================================


class TestResumeSessionContract:
    """resume_session must behave consistently across adapters."""

    @pytest.mark.parametrize("cls,factory", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_resume_returns_adapter_result(self, cls, factory):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (factory("resumed"), 0)
            result = _run(adapter.resume_session("sid-1", "Continue", working_dir="/tmp"))
        assert isinstance(result, AdapterResult)
        assert result.status == AdapterStatus.IDLE

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_resume_timeout(self, cls, _):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = TimeoutError()
            result = _run(
                adapter.resume_session(
                    "sid-1", "Continue", working_dir="/tmp", timeout_seconds=1.0
                )
            )
        assert result.status == AdapterStatus.TIMED_OUT

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_resume_error(self, cls, _):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("cli error", 1)
            result = _run(adapter.resume_session("sid-1", "Continue", working_dir="/tmp"))
        assert result.status == AdapterStatus.ERROR


# ===================================================================
# 4. is_available contract tests
# ===================================================================


class TestIsAvailableContract:
    """is_available must return bool for all adapters."""

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_returns_bool_when_available(self, cls, _):
        adapter = cls()
        with patch("shutil.which", return_value="/usr/bin/tool"):
            result = adapter.is_available()
        assert isinstance(result, bool)
        assert result is True

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_returns_bool_when_unavailable(self, cls, _):
        adapter = cls()
        with patch("shutil.which", return_value=None):
            result = adapter.is_available()
        assert isinstance(result, bool)
        assert result is False


# ===================================================================
# 5. Empty / edge-case prompt handling
# ===================================================================


class TestEmptyPromptHandling:
    """All adapters should handle empty prompts gracefully (no crash)."""

    @pytest.mark.parametrize("cls,factory", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_empty_prompt_does_not_raise(self, cls, factory):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (factory(""), 0)
            result = _run(adapter.send_prompt("", working_dir="/tmp"))
        assert isinstance(result, AdapterResult)

    @pytest.mark.parametrize("cls,factory", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_whitespace_only_prompt_does_not_raise(self, cls, factory):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (factory(""), 0)
            result = _run(adapter.send_prompt("   \n\t  ", working_dir="/tmp"))
        assert isinstance(result, AdapterResult)


# ===================================================================
# 6. Ollama functional adapter contract tests
# ===================================================================


class TestOllamaContract:
    """Ollama adapter uses module-level functions, not BaseAdapter subclass.

    We still verify it returns AdapterResult with valid status.
    """

    def test_run_returns_adapter_result_on_success(self):
        from agent_orchestrator.adapters.ollama_adapter import run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"Neutral memo output.", b"")
        mock_proc.returncode = 0
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(run("Summarize debate"))
        assert isinstance(result, AdapterResult)
        assert result.status == AdapterStatus.IDLE
        assert result.text == "Neutral memo output."
        assert result.session_id is None

    def test_run_timeout_returns_timed_out(self):
        from agent_orchestrator.adapters.ollama_adapter import OllamaAdapterConfig, run

        mock_proc = AsyncMock()
        mock_proc.communicate.side_effect = TimeoutError()
        mock_proc.kill = MagicMock()
        mock_proc.wait = AsyncMock()
        config = OllamaAdapterConfig(timeout_seconds=1)
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(run("Summarize", config=config))
        assert result.status == AdapterStatus.TIMED_OUT

    def test_run_error_returns_error_status(self):
        from agent_orchestrator.adapters.ollama_adapter import run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"model not found")
        mock_proc.returncode = 1
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(run("Summarize"))
        assert result.status == AdapterStatus.ERROR

    def test_run_empty_prompt_does_not_crash(self):
        from agent_orchestrator.adapters.ollama_adapter import run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"output", b"")
        mock_proc.returncode = 0
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(run(""))
        assert isinstance(result, AdapterResult)

    def test_check_available_returns_bool(self):
        from agent_orchestrator.adapters.ollama_adapter import check_available

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"NAME\nllama3.2:latest", b"")
        mock_proc.returncode = 0
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(check_available())
        assert isinstance(result, bool)


# ===================================================================
# 7. Normalize module integration with each adapter
# ===================================================================


class TestNormalizeIntegration:
    """normalize() and normalize_batch() work with AdapterResult from any adapter."""

    @pytest.mark.parametrize("cls,factory", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_normalize_success_result(self, cls, factory):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = (factory("adapter response"), 0)
            result = _run(adapter.send_prompt("Hi", working_dir="/tmp"))
        msg = normalize(result, agent_id="test-agent")
        assert isinstance(msg, NormalizedMessage)
        assert msg.agent_id == "test-agent"
        assert msg.status == "ok"
        assert "adapter response" in msg.text

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_normalize_timeout_result(self, cls, _):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.side_effect = TimeoutError()
            result = _run(adapter.send_prompt("Hi", working_dir="/tmp"))
        msg = normalize(result, agent_id="test-agent")
        assert msg.status == "timeout"

    @pytest.mark.parametrize("cls,_", CLASS_ADAPTERS, ids=["Claude", "Codex"])
    def test_normalize_error_result(self, cls, _):
        adapter = cls()
        with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = ("bad output", 1)
            result = _run(adapter.send_prompt("Hi", working_dir="/tmp"))
        msg = normalize(result, agent_id="test-agent")
        assert msg.status == "error"

    def test_normalize_ollama_result(self):
        from agent_orchestrator.adapters.ollama_adapter import run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"memo text", b"")
        mock_proc.returncode = 0
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = _run(run("Summarize"))
        msg = normalize(result, agent_id="ollama-memo")
        assert msg.status == "ok"
        assert msg.agent_id == "ollama-memo"

    def test_normalize_batch_mixed_results(self):
        """normalize_batch handles a mix of success, timeout, and error results."""
        results = [
            ("claude-1", AdapterResult(text="good result", status=AdapterStatus.IDLE)),
            ("codex-1", AdapterResult(text="timed out", status=AdapterStatus.TIMED_OUT)),
            ("ollama-1", AdapterResult(text="error output", status=AdapterStatus.ERROR)),
        ]
        msgs = normalize_batch(results)
        assert len(msgs) == 3
        assert msgs[0].status == "ok"
        assert msgs[0].agent_id == "claude-1"
        assert msgs[1].status == "timeout"
        assert msgs[1].agent_id == "codex-1"
        assert msgs[2].status == "error"
        assert msgs[2].agent_id == "ollama-1"

    def test_normalize_batch_empty_list(self):
        msgs = normalize_batch([])
        assert msgs == []

    def test_normalize_preserves_session_id(self):
        result = AdapterResult(text="data", session_id="sess-xyz", status=AdapterStatus.IDLE)
        msg = normalize(result, agent_id="a1")
        assert msg.session_id == "sess-xyz"

    def test_normalize_preserves_metadata(self):
        result = AdapterResult(
            text="data", status=AdapterStatus.IDLE, metadata={"model": "claude-4"}
        )
        msg = normalize(result, agent_id="a1")
        assert msg.metadata == {"model": "claude-4"}

    def test_normalize_token_count_is_word_count(self):
        result = AdapterResult(text="one two three", status=AdapterStatus.IDLE)
        msg = normalize(result, agent_id="a1")
        assert msg.token_count == 3


# ===================================================================
# 8. Cross-adapter contract: uniform return types
# ===================================================================


class TestCrossAdapterContract:
    """All adapters produce identical return types regardless of implementation."""

    def test_all_class_adapters_return_same_result_type(self):
        """Every class-based adapter returns the same AdapterResult type."""
        results = []
        for cls, factory in CLASS_ADAPTERS:
            adapter = cls()
            with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
                mock_run.return_value = (factory("test"), 0)
                result = _run(adapter.send_prompt("test", working_dir="/tmp"))
            results.append(result)
        assert all(type(r) is AdapterResult for r in results)

    def test_all_adapters_use_same_status_enum(self):
        """All adapters use AdapterStatus enum for status field."""
        results = []
        for cls, factory in CLASS_ADAPTERS:
            adapter = cls()
            with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
                mock_run.return_value = (factory("test"), 0)
                result = _run(adapter.send_prompt("test", working_dir="/tmp"))
            results.append(result)
        # Also include an Ollama result
        from agent_orchestrator.adapters.ollama_adapter import run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"test", b"")
        mock_proc.returncode = 0
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            results.append(_run(run("test")))

        for r in results:
            assert isinstance(r.status, AdapterStatus)

    def test_timeout_status_is_consistent_across_adapters(self):
        """All adapters return TIMED_OUT on timeout, regardless of implementation."""
        timeout_results = []
        for cls, _ in CLASS_ADAPTERS:
            adapter = cls()
            with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
                mock_run.side_effect = TimeoutError()
                result = _run(adapter.send_prompt("test", working_dir="/tmp"))
            timeout_results.append(result)
        # Ollama timeout
        from agent_orchestrator.adapters.ollama_adapter import OllamaAdapterConfig, run

        mock_proc = AsyncMock()
        mock_proc.communicate.side_effect = TimeoutError()
        mock_proc.kill = MagicMock()
        mock_proc.wait = AsyncMock()
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            timeout_results.append(
                _run(run("test", config=OllamaAdapterConfig(timeout_seconds=1)))
            )

        for r in timeout_results:
            assert r.status == AdapterStatus.TIMED_OUT

    def test_error_status_is_consistent_across_adapters(self):
        """All adapters return ERROR on CLI failure."""
        error_results = []
        for cls, _ in CLASS_ADAPTERS:
            adapter = cls()
            with patch.object(adapter, "_run_cli", new_callable=AsyncMock) as mock_run:
                mock_run.return_value = ("error output", 1)
                result = _run(adapter.send_prompt("test", working_dir="/tmp"))
            error_results.append(result)
        # Ollama error
        from agent_orchestrator.adapters.ollama_adapter import run

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"fail")
        mock_proc.returncode = 1
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            error_results.append(_run(run("test")))

        for r in error_results:
            assert r.status == AdapterStatus.ERROR
