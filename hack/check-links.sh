#!/bin/bash

set -euo pipefail

if [ "$#" -eq 0 ]; then
    echo "No Markdown files to check."
    exit 0
fi

LYCHEE_BIN=${LYCHEE_BIN:-lychee}

exec "$LYCHEE_BIN" \
    --format markdown \
    -E \
    --exclude-mail \
    -i \
    -n \
    -t 45 \
    -- \
    "$@"
