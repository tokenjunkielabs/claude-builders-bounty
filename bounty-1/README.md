# `/generate-changelog`

A dependency-free Claude Code skill and command-line generator for turning Git history into a structured `CHANGELOG.md`.

## Setup and use — three steps

1. Copy the `.claude/skills/generate-changelog` directory into the target repository.
2. Run `/generate-changelog` in Claude Code, or run `bash .claude/skills/generate-changelog/changelog.sh --repo "$PWD"`.
3. Review and commit the generated `CHANGELOG.md`.

## Behavior

By default, the generator reads non-merge commits after the latest reachable tag. In an untagged repository it reads all commits. It understands Conventional Commit prefixes and falls back to keyword classification:

| Changelog section | Recognized examples |
| --- | --- |
| Added | `feat:`, `feature:`, `add:`, “introduce”, “create” |
| Fixed | `fix:`, `bugfix:`, `hotfix:`, “repair”, “resolve” |
| Removed | `remove:`, `delete:`, `deprecate:` |
| Changed | `docs:`, `refactor:`, `perf:`, `chore:`, uncategorized subjects, breaking changes |

Every generated section contains `Added`, `Fixed`, `Changed`, and `Removed` headings. Re-running the command replaces only the marked generated section and retains older manual changelog content.

## Options

```text
--repo PATH          Git repository path (default: current directory)
--output PATH        Output file (default: CHANGELOG.md)
--since REVISION     Start after this revision instead of the latest tag
--version LABEL      Heading label (default: Unreleased)
--date YYYY-MM-DD    Heading date (default: current UTC date)
--include-merges     Include merge commits
--dry-run            Print without writing
```

The implementation uses only Python's standard library and invokes Git without a shell.
