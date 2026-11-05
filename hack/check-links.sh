#!/bin/bash

set -euo pipefail

if [ "$#" -eq 0 ]; then
    echo "No Markdown files to check."
    exit 0
fi

LYCHEE_BIN=${LYCHEE_BIN:-lychee}

# Lychee v0.11.1 treats paths containing ?, *, [, or ] as glob patterns.
# Escape those characters using the syntax from Rust's glob::Pattern::escape.
literal_paths=()
for path in "$@"; do
    escaped_path=""
    for ((index = 0; index < ${#path}; index++)); do
        character=${path:index:1}
        case "$character" in
            \? | \* | \[ | \]) escaped_path+="[$character]" ;;
            *) escaped_path+="$character" ;;
        esac
    done
    literal_paths+=("$escaped_path")
done

lychee_args=(
    --format markdown
    -E
    --exclude-mail
    -i
    -n
    -t 45
    --
    "${literal_paths[@]}"
)

if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    "$LYCHEE_BIN" "${lychee_args[@]}" | tee -a "$GITHUB_STEP_SUMMARY"
else
    exec "$LYCHEE_BIN" "${lychee_args[@]}"
fi
