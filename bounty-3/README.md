# Destructive command guard - bounty #3

A zero-dependency Claude Code `PreToolUse` hook that blocks destructive Bash/SQL commands before execution.

## Install

From the repository root:

```bash
chmod +x bounty-3/install.sh
./bounty-3/install.sh
```

The installer copies the guard to `~/.claude/hooks/destructive_command_guard.py` and merges a `PreToolUse` / `Bash` hook into `~/.claude/settings.json` without replacing unrelated settings.

## What it blocks

The guard denies a Bash tool call when it detects any of these operations:

- recursive forced deletion: `rm -rf`, `rm -fr`, split `rm -r -f`, and equivalent long flags;
- `DROP TABLE`;
- `git push --force`, `git push --force-with-lease`, or `git push -f`;
- `TRUNCATE` / `TRUNCATE TABLE`;
- `DELETE FROM ...` when the SQL statement has no `WHERE` clause.

Normal Bash commands produce no hook output and continue through Claude Code's normal permission flow.

## Block behavior

For a blocked call, the hook:

1. appends one JSON line to `~/.claude/hooks/blocked.log` containing the UTC timestamp, attempted command, project path, and block reason;
2. returns Claude Code's structured `PreToolUse` decision with `permissionDecision: "deny"`;
3. gives Claude a clear reason and asks it to use a non-destructive alternative.

Example log entry:

```json
{"timestamp":"2026-09-21T00:00:00+00:00","attempted_command":"git push --force origin main","project_path":"/workspace/app","reason":"Blocked forced git push."}
```

The hook uses the event's `cwd` as the project path and falls back to `CLAUDE_PROJECT_DIR` / the process working directory only when `cwd` is absent.

## Files

- `.claude/hooks/destructive_command_guard.py` - hook implementation.
- `install.sh` - idempotent installer and settings merger.

The implementation follows Claude Code's current command-hook contract: command hooks read the event JSON from stdin; `PreToolUse` may return `hookSpecificOutput.permissionDecision = "deny"` with a reason; exit 0 with no output leaves safe calls on the normal permission path.
