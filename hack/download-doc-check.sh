#!/usr/bin/env bash

set -euo pipefail

readonly upstream_ref="d715028e5fed35398192f2b51d707a1dd6806cd5"
readonly script_name="${1:-}"

case "$script_name" in
  check-file-encoding.py)
    readonly expected_sha256="a2adc4369a26ce912409f35c50ac7e3b5e649baa353ceb5c6f6af7463ff7da9c"
    ;;
  check-conflicts.py)
    readonly expected_sha256="34013cdfcf7930d87f8d604b2fa5e14e617ad7270d976c365b99194a0c6664ab"
    ;;
  check-control-char.py)
    readonly expected_sha256="0b5e806d2cd11b066153f0789ad27321357e9e4800c1fc682b8f646aa9dc9194"
    ;;
  check-tags.py)
    readonly expected_sha256="02779f185f89ec70b11ea73642d5b5c7208a10c32d99273f0d15967a70c6e815"
    ;;
  check-manual-line-breaks.py)
    readonly expected_sha256="c32d4c7284140e97dea140f6abea75270ad647b613986d393c9b004b5ac14c06"
    ;;
  *)
    echo "Unsupported documentation check: $script_name" >&2
    exit 1
    ;;
esac

curl --fail --location --silent --show-error \
  --retry 3 --retry-all-errors --connect-timeout 15 --max-time 60 \
  --output "$script_name" \
  "https://raw.githubusercontent.com/pingcap/docs/${upstream_ref}/scripts/${script_name}"
printf '%s  %s\n' "$expected_sha256" "$script_name" | sha256sum --check
