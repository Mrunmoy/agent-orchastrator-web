"""Ollama memo adapter for neutral decision memo generation.

Unlike the class-based Claude/Codex adapters (debate participants), the Ollama
adapter is stateless and uses module-level functions.  It calls the Ollama CLI
to summarise or analyse debate progress from a neutral perspective.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass

from agent_orchestrator.adapters.base import AdapterResult, AdapterStatus


@dataclass
class OllamaAdapterConfig:
    """Configuration for the Ollama memo adapter."""

    model: str = "llama3.2"
    host: str = "http://localhost:11434"
    timeout_seconds: float = 120


async def run(
    prompt: str,
    *,
    config: OllamaAdapterConfig | None = None,
) -> AdapterResult:
    """Run an Ollama model to generate a neutral memo.

    The prompt is sent via stdin to ``ollama run <model>``.
    Returns an :class:`AdapterResult` with ``session_id`` always ``None``.
    """
    cfg = config or OllamaAdapterConfig()
    env = {**os.environ, "OLLAMA_HOST": cfg.host}

    try:
        proc = await asyncio.create_subprocess_exec(
            "ollama",
            "run",
            cfg.model,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
    except FileNotFoundError:
        return AdapterResult(
            text="Ollama CLI not found",
            session_id=None,
            status=AdapterStatus.ERROR,
            metadata={"stderr": "ollama: command not found"},
        )

    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(input=prompt.encode()),
            timeout=cfg.timeout_seconds,
        )
    except TimeoutError:
        proc.kill()
        await proc.wait()
        return AdapterResult(
            text="Ollama CLI timed out",
            session_id=None,
            status=AdapterStatus.TIMED_OUT,
        )

    stdout = stdout_bytes.decode()
    stderr = stderr_bytes.decode()

    if proc.returncode != 0:
        return AdapterResult(
            text=stdout or "Ollama CLI returned a non-zero exit code",
            session_id=None,
            status=AdapterStatus.ERROR,
            metadata={"stderr": stderr} if stderr else {},
        )

    return AdapterResult(
        text=stdout,
        session_id=None,
        status=AdapterStatus.IDLE,
    )


async def check_available(
    *,
    config: OllamaAdapterConfig | None = None,
) -> bool:
    """Check whether the Ollama CLI is reachable by running ``ollama list``."""
    cfg = config or OllamaAdapterConfig()
    env = {**os.environ, "OLLAMA_HOST": cfg.host}

    try:
        proc = await asyncio.create_subprocess_exec(
            "ollama",
            "list",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        await proc.communicate()
        return proc.returncode == 0
    except (FileNotFoundError, OSError):
        return False
