# Claude PR Reviewer

`claude-review` is a dependency-free Python CLI that fetches a GitHub pull-request diff, gives that diff to Claude Code in non-interactive mode, and emits a stable Markdown review contract.

It implements bounty #4: <https://github.com/claude-builders-bounty/claude-builders-bounty/issues/4>.

## Requirements

- Python 3.10+
- Claude Code installed and authenticated so `claude -p` works
- Network access to GitHub
- Optional `GITHUB_TOKEN` for private repositories or higher GitHub API limits

## Install

From this repository checkout:

```bash
mkdir -p ~/.local/bin
install -m 755 agents/pr-reviewer/claude-review ~/.local/bin/claude-review
```

Ensure `~/.local/bin` is on `PATH`.

## Usage

```bash
claude-review --pr https://github.com/owner/repo/pull/123
```

Write the review to a file:

```bash
claude-review --pr https://github.com/owner/repo/pull/123 --output review.md
```

For a private PR:

```bash
export GITHUB_TOKEN=ghp_your_token
claude-review --pr https://github.com/private-owner/private-repo/pull/123
```

If the Claude Code executable is not named `claude`, set `CLAUDE_BIN` or pass `--claude-bin`.

## Output contract

The command rejects model output that does not contain these sections in order:

```markdown
## Summary
Two or three sentences.

## Identified Risks
- ...

## Improvement Suggestions
- ...

## Confidence
High
```

Confidence must be exactly `Low`, `Medium`, or `High`. Risks and suggestions must each contain a Markdown bullet.

## Safety and failure behavior

Pull-request text and diff contents are explicitly framed as untrusted input. The review prompt tells Claude never to execute or follow instructions embedded in code, comments, documentation, filenames, or the diff itself.

The CLI uses `subprocess.run(..., shell=False)`, passes the PR payload over stdin, and never evaluates content from the diff. GitHub requests use the REST API directly through Python's standard library.

Large diffs are rejected rather than silently truncated. The default limit is 750,000 bytes and can be changed with `--max-diff-bytes`.

The command exits non-zero on malformed PR URLs, GitHub failures, oversized/non-UTF-8 diffs, Claude Code failures/timeouts, empty output, or an invalid Markdown contract.

## Real-PR review samples

The bounty requires outputs from at least two real GitHub pull requests. Captured review artifacts are included under `examples/` with the exact PR URL and reviewed head SHA:

- `examples/claude-builders-bounty-4371.md` — the $100 destructive-command hook carrier.
- `examples/dokploy-5491.md` — Dokploy's generic-rclone backup-destination carrier.

These files use the exact output contract emitted by the CLI and are pinned to the head SHA listed in each sample so future changes to either PR do not make the recorded review ambiguous.

## Design notes

The CLI deliberately keeps GitHub retrieval and Claude execution separate. It does not post comments or mutate the reviewed repository; stdout (or `--output`) is the review artifact, leaving publication under the operator's normal GitHub permissions and review workflow.

No third-party Python packages are required.
