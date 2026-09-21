#!/usr/bin/env python3
"""Claude Code PreToolUse guard for destructive Bash commands."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shlex
import sys
from datetime import datetime, timezone


LOG_PATH = Path.home() / ".claude" / "hooks" / "blocked.log"


def _shell_words(fragment: str) -> list[str]:
    try:
        return shlex.split(fragment, posix=True)
    except ValueError:
        return fragment.split()


def _rm_is_recursive_and_forced(command: str) -> bool:
    for match in re.finditer(r"(?<![\w-])rm\b([^;&|\n]*)", command):
        recursive = False
        forced = False
        for token in _shell_words(match.group(1)):
            if token == "--":
                break
            if token == "--recursive":
                recursive = True
            elif token == "--force":
                forced = True
            elif token.startswith("-") and not token.startswith("--"):
                flags = token[1:]
                recursive = recursive or "r" in flags or "R" in flags
                forced = forced or "f" in flags
        if recursive and forced:
            return True
    return False


def _git_push_is_forced(command: str) -> bool:
    for match in re.finditer(r"(?<![\w-])git\s+push\b([^;&|\n]*)", command, re.IGNORECASE):
        for token in _shell_words(match.group(1)):
            if token in {"--force", "-f"} or token.startswith("--force="):
                return True
    return False


def _delete_without_where(command: str) -> bool:
    for match in re.finditer(
        r"\bDELETE\s+FROM\b(?P<body>[^;]*)(?:;|$)",
        command,
        re.IGNORECASE | re.DOTALL,
    ):
        if not re.search(r"\bWHERE\b", match.group("body"), re.IGNORECASE):
            return True
    return False


def destructive_reason(command: str) -> str | None:
    if _rm_is_recursive_and_forced(command):
        return "recursive forced deletion (rm -rf)"
    if re.search(r"\bDROP\s+TABLE\b", command, re.IGNORECASE):
        return "SQL DROP TABLE"
    if _git_push_is_forced(command):
        return "forced git push"
    if re.search(r"\bTRUNCATE(?:\s+TABLE)?\b", command, re.IGNORECASE):
        return "SQL TRUNCATE"
    if _delete_without_where(command):
        return "SQL DELETE FROM without a WHERE clause"
    return None


def _log_block(command: str, cwd: str, reason: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "project_path": cwd,
        "reason": reason,
    }
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0

    command = tool_input.get("command")
    if not isinstance(command, str) or not command.strip():
        return 0

    reason = destructive_reason(command)
    if reason is None:
        return 0

    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        cwd = os.getcwd()

    _log_block(command, cwd, reason)
    decision = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"Blocked destructive Bash command: {reason}. "
                f"The attempt was logged to {LOG_PATH}."
            ),
        }
    }
    sys.stdout.write(json.dumps(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
