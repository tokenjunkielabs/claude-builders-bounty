# Claude PR Review Agent — bounty #4

`claude-review` is a small Claude Code agent that accepts a GitHub pull-request
URL, fetches the PR metadata and patch from GitHub, asks the local Claude Code
CLI for a security/correctness-focused review, and prints a strict Markdown
review contract.

## Install

Requirements: Python 3.10+ and an authenticated Claude Code CLI (`claude`).

```bash
python3 -m pip install -e ./bounty-4
```

For private repositories or higher GitHub API limits, also export a GitHub token:

```bash
export GITHUB_TOKEN=github_pat_or_token
```

No third-party Python package is required.

## Use

```bash
claude-review --pr https://github.com/owner/repo/pull/123
```

Write the same Markdown to a file as well:

```bash
claude-review --pr https://github.com/owner/repo/pull/123 --output review.md
```

If the Claude Code executable has a different name/path:

```bash
export CLAUDE_REVIEW_CLAUDE_BIN=/path/to/claude
```

## Output contract

Every successful review contains exactly:

```markdown
## Summary
Two or three sentences.

## Identified Risks
- ...

## Improvement Suggestions
- ...

## Confidence
Low
```

`Confidence` is restricted to `Low`, `Medium`, or `High`. The CLI rejects a
Claude response that omits or reorders the required sections.

## What the agent reviews

The CLI retrieves:

- PR title/body/base/head metadata;
- every changed-file page from GitHub (100 files per page);
- textual patches, with an explicit marker when GitHub omits binary/oversized
  patch content.

Review input is bounded to 90,000 patch characters so a very large PR cannot
silently create an unbounded Claude prompt. The review prompt prioritizes
correctness, regressions, security, data loss, compatibility breaks, and error
handling.

## Prompt-injection boundary

PR content is hostile input. The prompt explicitly treats the PR title, body,
filenames, comments, code, and patch as untrusted repository data and tells
Claude never to follow instructions found inside them. The CLI never evaluates
PR code and never invokes a shell with repository-controlled text.

The Claude executable is launched with an argument vector (`shell=False`), so a
PR cannot turn diff text into a local shell command.

## GitHub authentication

Public PRs work without a token subject to GitHub's anonymous API limits. Set
`GITHUB_TOKEN` for private PRs you are allowed to access or for authenticated
rate limits. The token is sent only to `api.github.com`.

## Real-PR review examples

Two structured examples based on exact public PR patches are included:

- [`samples/claude-builders-bounty-4371.md`](samples/claude-builders-bounty-4371.md)
- [`samples/pocketpay-mobile-547.md`](samples/pocketpay-mobile-547.md)

They demonstrate the required review shape on two real GitHub pull requests
rather than synthetic diffs.
