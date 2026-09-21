# Example review: claude-builders-bounty/claude-builders-bounty#4371

Source PR: https://github.com/claude-builders-bounty/claude-builders-bounty/pull/4371

## Summary
This PR adds a Claude Code `PreToolUse` guard, an installer, and documentation for blocking destructive Bash and SQL operations before execution. The implementation separates command classification from the hook response and preserves the normal permission path when no destructive pattern is found.

## Identified Risks
- The `unwrap()` helper consumes option-looking arguments for `env`, `sudo`, and `doas` without modeling options that themselves take a following value. A command such as `env -u NAME rm -rf target` can leave `NAME` in command position and prevent the later `rm` classifier from seeing the destructive command.
- SQL detection searches the entire client command once a recognized SQL client is in command position. That can conservatively block SQL keywords appearing in non-query arguments or literal text, which is safer than a miss but can create false positives for legitimate tooling.

## Improvement Suggestions
- Parse wrapper options that consume values (`env -u NAME`, selected `sudo`/`doas` forms) before choosing the effective command token, then reuse that normalized command for every classifier.
- When a SQL client is detected, isolate its actual query argument/stdin contract where practical before applying `DROP TABLE`, `TRUNCATE`, and unbounded `DELETE FROM` checks; document any intentionally conservative fallback.

## Confidence
High
