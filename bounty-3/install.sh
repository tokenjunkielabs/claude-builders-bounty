#!/usr/bin/env bash
set -euo pipefail

HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
HOOK_DIR="${HOME}/.claude/hooks"
HOOK_PATH="${HOOK_DIR}/destructive_command_guard.py"
SETTINGS_PATH="${HOME}/.claude/settings.json"

mkdir -p "$HOOK_DIR"
install -m 700 "$HERE/.claude/hooks/destructive_command_guard.py" "$HOOK_PATH"

HOOK_PATH="$HOOK_PATH" SETTINGS_PATH="$SETTINGS_PATH" python3 - <<'PY'
import json
import os
from pathlib import Path
import sys

hook_path = Path(os.environ["HOOK_PATH"]).resolve()
settings_path = Path(os.environ["SETTINGS_PATH"])
settings_path.parent.mkdir(parents=True, exist_ok=True)

if settings_path.exists():
    with settings_path.open("r", encoding="utf-8") as handle:
        settings = json.load(handle)
else:
    settings = {}

hooks = settings.setdefault("hooks", {})
pre_tool_use = hooks.setdefault("PreToolUse", [])

needle = str(hook_path)
already_present = False
for group in pre_tool_use:
    if not isinstance(group, dict):
        continue
    for handler in group.get("hooks", []):
        if not isinstance(handler, dict):
            continue
        command = str(handler.get("command", ""))
        args = [str(arg) for arg in handler.get("args", [])]
        if needle == command or needle in args:
            already_present = True
            break
    if already_present:
        break

if not already_present:
    pre_tool_use.append(
        {
            "matcher": "Bash",
            "hooks": [
                {
                    "type": "command",
                    "command": sys.executable,
                    "args": [needle],
                }
            ],
        }
    )

tmp = settings_path.with_suffix(settings_path.suffix + ".tmp")
with tmp.open("w", encoding="utf-8") as handle:
    json.dump(settings, handle, indent=2)
    handle.write("\n")
os.replace(tmp, settings_path)
PY

printf 'Installed destructive-command guard at %s\n' "$HOOK_PATH"
printf 'Configured PreToolUse Bash hook in %s\n' "$SETTINGS_PATH"
