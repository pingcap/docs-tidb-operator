#!/usr/bin/env bash

set -euo pipefail

readonly checker="${1:-}"
readonly range="${2:-}"
shift 2

case "$checker" in
    check-file-encoding.py | check-conflicts.py | check-control-char.py | check-tags.py | check-manual-line-breaks.py) ;;
    *)
        echo "Unsupported documentation check: $checker" >&2
        exit 1
        ;;
esac

case "$range" in
    '..' | '...') ;;
    *)
        echo "Unsupported Git revision range: $range" >&2
        exit 1
        ;;
esac

: "${BASE_REF:?BASE_REF must be set}"
: "${RUNNER_TEMP:?RUNNER_TEMP must be set}"

changed_list="$(mktemp "$RUNNER_TEMP/changed-docs.XXXXXX")"
trap 'rm -f "$changed_list"' EXIT

git diff-tree --name-only --no-commit-id -z -r \
    "upstream/${BASE_REF}${range}HEAD" -- "$@" > "$changed_list"

changed_files=()
while IFS= read -r -d '' changed_file; do
    changed_files+=("./$changed_file")
done < "$changed_list"

if (( ${#changed_files[@]} == 0 )); then
    echo "No matching changed files to check."
    exit 0
fi

python3 "$checker" "${changed_files[@]}"
