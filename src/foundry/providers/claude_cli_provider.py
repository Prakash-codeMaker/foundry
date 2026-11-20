"""Planning provider via the `claude` command (text only, no tools)."""

from __future__ import annotations

import shutil
import subprocess
import tempfile

from foundry import constants, procenv
from foundry.providers.base import LLMProvider


class ClaudeCliProvider(LLMProvider):
    name = "claude_cli"

    def __init__(self) -> None:
        self._bin = shutil.which("claude")

    def is_available(self) -> bool:
        return self._bin is not None

    def complete(self, system: str, user: str, seat: str = "planner") -> str:
        if self._bin is None:
            raise RuntimeError("claude CLI not found on PATH")
        cmd = [self._bin, "-p", "--output-format", "text", "--system-prompt", system]
        model = constants.seat_model(seat, override=constants.CLI_MODEL)
        if model:
            cmd += ["--model", model]
        with tempfile.TemporaryDirectory(prefix="foundry-plan-") as workdir:
            proc = subprocess.run(
                cmd,
                input=user,
                capture_output=True,
                text=True,
                timeout=constants.PLAN_TIMEOUT,
                cwd=workdir,
                env=procenv.clean_env(),
            )
        if proc.returncode != 0:
            detail = "\n".join(
                part.strip()[:300]
                for part in (proc.stdout, proc.stderr)
                if part and part.strip()
            )
            raise RuntimeError(
                f"claude CLI failed ({proc.returncode}): {detail[:600]}"
            )
        return proc.stdout
