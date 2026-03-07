"""Codex CLI adapter for the agent orchestrator."""

from __future__ import annotations

import asyncio
import json
import shutil

from agent_orchestrator.adapters.base import AdapterResult, AdapterStatus, BaseAdapter


class CodexAdapter(BaseAdapter):
    """Adapter that drives the Codex CLI (codex command)."""

    def is_available(self) -> bool:
        return shutil.which("codex") is not None

    async def send_prompt(
        self,
        prompt: str,
        *,
        working_dir: str,
        session_id: str | None = None,
        timeout_seconds: float = 120.0,
    ) -> AdapterResult:
        cmd = self._build_command(prompt, session_id=session_id)
        try:
            stdout, returncode = await self._run_cli(cmd, working_dir, timeout_seconds)
        except TimeoutError:
            return AdapterResult(
                text="Codex CLI timed out",
                status=AdapterStatus.TIMED_OUT,
            )
        return self._parse_output(stdout, returncode)

    async def resume_session(
        self,
        session_id: str,
        prompt: str,
        *,
        working_dir: str,
        timeout_seconds: float = 120.0,
    ) -> AdapterResult:
        cmd = self._build_command(prompt, session_id=session_id)
        try:
            stdout, returncode = await self._run_cli(cmd, working_dir, timeout_seconds)
        except TimeoutError:
            return AdapterResult(
                text="Codex CLI timed out",
                session_id=session_id,
                status=AdapterStatus.TIMED_OUT,
            )
        return self._parse_output(stdout, returncode)

    def _build_command(self, prompt: str, *, session_id: str | None = None) -> list[str]:
        cmd = ["codex", "--json"]
        if session_id:
            cmd.extend(["--session", session_id])
        cmd.append(prompt)
        return cmd

    def _parse_output(self, stdout: str, returncode: int) -> AdapterResult:
        if returncode != 0:
            return AdapterResult(
                text=stdout or "Codex CLI returned a non-zero exit code",
                status=AdapterStatus.ERROR,
            )
        try:
            data = json.loads(stdout)
        except (json.JSONDecodeError, TypeError):
            return AdapterResult(
                text=f"Failed to parse Codex CLI output: {stdout}",
                status=AdapterStatus.ERROR,
            )
        text = self._extract_text(data)
        return AdapterResult(
            text=text,
            session_id=data.get("id"),
            status=AdapterStatus.IDLE,
            metadata={k: v for k, v in data.items() if k not in ("id", "output")},
        )

    def _extract_text(self, data: dict) -> str:
        parts: list[str] = []
        for item in data.get("output", []):
            if item.get("type") != "message":
                continue
            for block in item.get("content", []):
                if block.get("type") == "output_text":
                    parts.append(block.get("text", ""))
        return "".join(parts)

    async def _run_cli(
        self, cmd: list[str], working_dir: str, timeout_seconds: float
    ) -> tuple[str, int]:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=working_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
        except TimeoutError:
            proc.kill()
            await proc.wait()
            raise
        return stdout_bytes.decode(), proc.returncode
