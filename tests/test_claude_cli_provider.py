from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest

from foundry.providers.claude_cli_provider import ClaudeCliProvider


def test_cli_failure_includes_stdout_when_stderr_is_empty() -> None:
    provider = ClaudeCliProvider()
    provider._bin = "claude"
    result = subprocess.CompletedProcess(
        args=["claude"], returncode=1, stdout="Login expired", stderr=""
    )
    with patch("foundry.providers.claude_cli_provider.subprocess.run", return_value=result):
        with pytest.raises(RuntimeError, match="Login expired"):
            provider.complete("system", "user")


def test_cli_failure_includes_stderr_and_stdout() -> None:
    provider = ClaudeCliProvider()
    provider._bin = "claude"
    result = subprocess.CompletedProcess(
        args=["claude"], returncode=1, stdout="Login expired", stderr="CLI error"
    )
    with patch("foundry.providers.claude_cli_provider.subprocess.run", return_value=result):
        with pytest.raises(RuntimeError) as error:
            provider.complete("system", "user")
    assert "CLI error" in str(error.value)
    assert "Login expired" in str(error.value)
