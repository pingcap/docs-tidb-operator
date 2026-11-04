#!/bin/bash
#
# In addition to verify-links.sh, this script additionally check anchors.
#
# Dependencies are installed exactly from the committed package-lock.json.

set -euo pipefail

ROOT=$(unset CDPATH && cd $(dirname "${BASH_SOURCE[0]}")/.. && pwd)
cd $ROOT

npm ci --ignore-scripts

echo "info: checking links anchors under $ROOT directory..."

npx --no-install remark --ignore-path .gitignore -u lint -u @breeswish-org/remark-lint-pingcap-docs-anchor . --frail --quiet
