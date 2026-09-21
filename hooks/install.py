#!/usr/bin/env python3
"""Install the destructive-command PreToolUse guard in user Claude Code settings."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "pre_tool_use_guard.py"
CLAUDE_DIR = Path.home() / ".claude"
HOOK_DIR = CLAUDE_DIR / "hooks"
DEST = HOOK_DIR / "pre_tool_use_guard.py"
SETTINGS = CLAUDE_DIR / "settings.json"
COMMAND = 'python3 "${HOME}/.claude/hooks/pre_tool_use_guard.py"'


def load_settings() -> dict:
    if not SETTINGS.exists():
        return {}
    try:
        data = json.loads(SETTINGS.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Refusing to overwrite invalid JSON in {SETTINGS}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Refusing to overwrite non-object JSON in {SETTINGS}")
    return data


def hook_present(entries: list) -> bool:
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        for handler in entry.get("hooks", []):
            if isinstance(handler, dict) and handler.get("command") == COMMAND:
                return True
    return False


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> None:
    HOOK_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, DEST)
    DEST.chmod(0o755)

    settings = load_settings()
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise SystemExit(f"Expected {SETTINGS} hooks to be an object")

    pre_tool = hooks.setdefault("PreToolUse", [])
    if not isinstance(pre_tool, list):
        raise SystemExit(f"Expected {SETTINGS} hooks.PreToolUse to be an array")

    if not hook_present(pre_tool):
        pre_tool.append(
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": COMMAND,
                    }
                ],
            }
        )

    atomic_write_json(SETTINGS, settings)
    print(f"Installed guard: {DEST}")
    print(f"Updated settings: {SETTINGS}")


if __name__ == "__main__":
    main()
