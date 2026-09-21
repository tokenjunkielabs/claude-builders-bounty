#!/usr/bin/env bash
# Generate a Keep-a-Changelog-style CHANGELOG.md from Git history.
set -euo pipefail

ORIGINAL_DIR=$PWD

if ! REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null); then
  printf 'changelog.sh: run this command inside a Git repository\n' >&2
  exit 2
fi

if (($# > 1)); then
  printf 'usage: bash changelog.sh [OUTPUT_PATH]\n' >&2
  exit 2
fi

if (($# == 1)); then
  if [[ $1 = /* ]]; then
    OUTPUT=$1
  else
    OUTPUT=$ORIGINAL_DIR/$1
  fi
else
  OUTPUT=$REPO_ROOT/CHANGELOG.md
fi

cd "$REPO_ROOT"

LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || true)
if [[ -n $LAST_TAG ]]; then
  RANGE="${LAST_TAG}..HEAD"
  RANGE_NOTE="Commits since \`${LAST_TAG}\`."
else
  RANGE="HEAD"
  RANGE_NOTE="All reachable commits (no Git tag was found)."
fi

ADDED=()
FIXED=()
CHANGED=()
REMOVED=()

while IFS=$'\x1f' read -r HASH SUBJECT; do
  [[ -n $HASH ]] || continue

  PREFIX=$SUBJECT
  if [[ $SUBJECT == *:* ]]; then
    PREFIX=${SUBJECT%%:*}
  fi
  KIND=${PREFIX%%\(*}
  KIND=${KIND%!}
  KIND=$(printf '%s' "$KIND" | tr '[:upper:]' '[:lower:]')

  DISPLAY=$SUBJECT
  case "$KIND" in
    feat|feature|add|added|new|fix|fixed|bug|bugfix|hotfix|remove|removed|delete|deleted|deprecate|deprecated|change|changed|refactor|perf|docs|chore|build|ci|test|style|revert)
      if [[ $SUBJECT == *:* ]]; then
        DISPLAY=${SUBJECT#*:}
        # Trim leading whitespace after a recognized conventional-commit prefix.
        DISPLAY="${DISPLAY#"${DISPLAY%%[![:space:]]*}"}"
      fi
      ;;
  esac

  FIRST_WORD=$(printf '%s' "$SUBJECT" | awk '{print tolower($1)}')
  [[ -n $DISPLAY ]] || DISPLAY=$SUBJECT
  ENTRY="- ${DISPLAY} (\`${HASH}\`)"

  case "$KIND" in
    feat|feature|add|added|new)
      ADDED+=("$ENTRY")
      ;;
    fix|fixed|bug|bugfix|hotfix)
      FIXED+=("$ENTRY")
      ;;
    remove|removed|delete|deleted|deprecate|deprecated)
      REMOVED+=("$ENTRY")
      ;;
    *)
      case "$FIRST_WORD" in
        add|added|new)
          ADDED+=("$ENTRY")
          ;;
        fix|fixed|bugfix)
          FIXED+=("$ENTRY")
          ;;
        remove|removed|delete|deleted)
          REMOVED+=("$ENTRY")
          ;;
        *)
          CHANGED+=("$ENTRY")
          ;;
      esac
      ;;
  esac
done < <(git log "$RANGE" --format='%h%x1f%s')

emit_section() {
  local TITLE=$1
  shift
  printf '### %s\n' "$TITLE"
  if (($#)); then
    printf '%s\n' "$@"
  else
    printf '%s\n' '- None.'
  fi
  printf '\n'
}

mkdir -p "$(dirname "$OUTPUT")"
TMP="${OUTPUT}.tmp.$$"
trap 'rm -f "$TMP"' EXIT

{
  printf '# Changelog\n\n'
  printf 'All notable changes to this project are documented in this file.\n\n'
  printf '## [Unreleased] - %s\n\n' "$(date -u +%F)"
  printf '%s\n\n' "$RANGE_NOTE"
  emit_section 'Added' "${ADDED[@]}"
  emit_section 'Fixed' "${FIXED[@]}"
  emit_section 'Changed' "${CHANGED[@]}"
  emit_section 'Removed' "${REMOVED[@]}"
} > "$TMP"

mv "$TMP" "$OUTPUT"
trap - EXIT
printf 'Wrote %s\n' "$OUTPUT"
