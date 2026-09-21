# Destructive-command PreToolUse guard

A Claude Code `PreToolUse` hook that denies destructive Bash commands before they execute while leaving ordinary Bash calls alone.

## Install

From this repository checkout:

```bash
python3 hooks/install.py
```

That single command copies the guard to `~/.claude/hooks/pre_tool_use_guard.py`, makes it executable, and merges a Bash `PreToolUse` handler into `~/.claude/settings.json` without replacing existing hooks.

## Blocked commands

The guard denies:

- recursive forced `rm` deletion, including `rm -rf`, `rm -fr`, and split `-r -f` flags;
- `DROP TABLE`;
- `git push --force` and `git push -f`;
- `TRUNCATE` / `TRUNCATE TABLE`;
- `DELETE FROM ...` statements that have no `WHERE` clause.

Matching is restricted to Claude Code's `Bash` tool. If none of those patterns is present, the hook exits successfully without returning a decision, so Claude Code's normal permission flow remains unchanged.

## Block record and Claude-facing reason

Every blocked attempt is appended as one JSON object per line to:

```text
~/.claude/hooks/blocked.log
```

Each record contains an ISO-8601 UTC timestamp, the attempted command, the project path supplied by Claude Code, and the block reason.

For a block, the hook returns the current structured `PreToolUse` decision format:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked destructive Bash command: …"
  }
}
```

The denial reason is therefore delivered directly to Claude rather than being emitted as unrelated stdout text.

## Files

- `pre_tool_use_guard.py` — stdin JSON parser, destructive-command policy, append-only audit log, and deny decision.
- `install.py` — idempotent user-level installer that preserves existing settings and refuses to overwrite invalid/non-object JSON.
