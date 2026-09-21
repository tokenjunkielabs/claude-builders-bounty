#!/usr/bin/env python3
"""Claude Code PreToolUse guard for destructive Bash commands.

Reads the Claude Code hook payload from stdin. Safe Bash calls emit no output
and exit 0. Dangerous calls return a PreToolUse deny decision and are appended
to ~/.claude/hooks/blocked.log.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


RM_COMMAND = re.compile(r"(?im)(?:^|[;&|]\\s*)(?:sudo\\s+)?rm\\s+(?P<args>[^;&|\\n]*)")
DROP_TABLE = re.compile(r"(?i)\\bDROP\\s+TABLE\\b")
TRUNCATE = re.compile(r"(?i)\\bTRUNCATE(?:\\s+TABLE)?\\b")
GIT_FORCE_PUSH = re.compile(
    r"(?i)\\bgit(?:\\s+-C\\s+(?:'[^']*'|\\\"[^\\\"]*\\\"|\\S+))?\\s+push\\b"
    r"(?P<args>[^;&|\\n]*)"
)
DELETE_FROM = re.compile(r"(?i)\\bDELETE\\s+FROM\\b")


def _rm_is_recursive_and_forced(command: str) -> bool:
    """Recognize rm -rf / -fr and split -r -f variants."""
    for match in RM_COMMAND.finditer(command):
        args = match.group("args")
        short_flags: set[str] = set()
        long_recursive = False
        long_force = False
        for token in re.findall(r"(?:'[^']*'|\\\"[^\\\"]*\\\"|\\S+)", args):
            token = token.strip("'\\\"")
            if token == "--":
                break
            if token == "--recursive":
                long_recursive = True
            elif token == "--force":
                long_force = True
            elif token.startswith("-") and not token.startswith("--"):
                short_flags.update(token[1:])
            elif not token.startswith("-"):
                continue
        if ("r" in short_flags or "R" in short_flags or long_recursive) and (
            "f" in short_flags or long_force
        ):
            return True
    return False


def _git_push_is_forced(command: str) -> bool:
    for match in GIT_FORCE_PUSH.finditer(command):
        args = match.group("args")
        if re.search(r"(?i)(?:^|\\s)--force(?:-with-lease|-if-includes)?(?:=|\\s|$)", args):
            return True
        if re.search(r"(?:^|\\s)-f(?:\\s|$)", args):
            return True
    return False


def _delete_without_where(command: str) -> bool:
    """Find each DELETE FROM statement and require WHERE before its boundary."""
    for match in DELETE_FROM.finditer(command):
        tail = command[match.end() :]
        boundary = len(tail)
        for marker in (";", "\n"):
            pos = tail.find(marker)
            if pos >= 0:
                boundary = min(boundary, pos)
        statement_tail = tail[:boundary]
        if re.search(r"(?i)\\bWHERE\\b", statement_tail) is None:
            return True
    return False


def danger_reason(command: str) -> str | None:
    if _rm_is_recursive_and_forced(command):
        return "Blocked recursive forced deletion (rm with both recursive and force flags)."
    if DROP_TABLE.search(command):
        return "Blocked SQL DROP TABLE command."
    if _git_push_is_forced(command):
        return "Blocked forced git push."
    if TRUNCATE.search(command):
        return "Blocked SQL TRUNCATE command."
    if _delete_without_where(command):
        return "Blocked SQL DELETE FROM without a WHERE clause."
    return None


def project_path(payload: dict[str, Any]) -> str:
    value = payload.get("cwd")
    if isinstance(value, str) and value:
        return value
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def append_block_log(command: str, project: str, reason: str) -> None:
    log_dir = Path.home() / ".claude" / "hooks"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "blocked.log"
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    record = {
        "timestamp": timestamp,
        "attempted_command": command,
        "project_path": project,
        "reason": reason,
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError) as exc:
        deny(f"Command blocked because the safety hook could not parse its input: {exc}")
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        deny("Command blocked because the Bash hook payload is missing tool_input.")
        return 0

    command = tool_input.get("command")
    if not isinstance(command, str):
        deny("Command blocked because the Bash hook payload has no command string.")
        return 0

    reason = danger_reason(command)
    if reason is None:
        return 0

    project = project_path(payload)
    try:
        append_block_log(command, project, reason)
    except OSError as exc:
        deny(f"{reason} The block log could not be written: {exc}")
        return 0

    deny(f"{reason} Review the command and use a non-destructive alternative.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
