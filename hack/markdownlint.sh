#!/bin/bash
#
# This script runs markdownlint according to ./.markdownlint.yaml.
#
# It replaces avto-dev/markdown-lint to avoid multiple setups of node.js environment.
#
# See https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally if you meet permission problems when executing npm install.

set -euo pipefail

ROOT=$(unset CDPATH && cd $(dirname "${BASH_SOURCE[0]}")/.. && pwd)
cd $ROOT

npm --loglevel=error install markdownlint-cli@0.26.0
echo "info: running markdownlint under $ROOT directory..."
npx markdownlint -c ./.markdownlint.yaml -i node_modules .
