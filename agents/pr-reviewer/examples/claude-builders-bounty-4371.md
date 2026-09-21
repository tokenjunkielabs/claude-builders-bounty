# Real PR sample: claude-builders-bounty #4371

- PR: https://github.com/claude-builders-bounty/claude-builders-bounty/pull/4371
- Reviewed head: `125b47fd5ec9ab496bf528a7e2661096d91af44c`
- Bounty: https://github.com/claude-builders-bounty/claude-builders-bounty/issues/3

## Summary
This PR adds a Python Claude Code `PreToolUse` guard that denies required destructive Bash, Git, and SQL command patterns and records each denial in a local audit log. It also adds an installer that preserves existing Claude settings plus documentation for setup, blocked-command behavior, and log location.

## Identified Risks
- The guard is intentionally pattern-based rather than a complete shell interpreter, so commands assembled dynamically at runtime or hidden inside external scripts remain outside its stated protection boundary.
- The audit log is a local append-only file under the user's home directory; concurrent hook invocations rely on the operating system's append behavior rather than an explicit file lock.

## Improvement Suggestions
- Keep the pattern guard's threat-model limitation prominent in the README so operators do not treat it as a complete shell sandbox.
- If high-concurrency hook execution becomes common, consider serializing or otherwise hardening concurrent writes to `blocked.log`.

## Confidence
High
