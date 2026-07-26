#!/usr/bin/env bash
# Install gstack (https://github.com/garrytan/gstack) for use with this repo.
# Usage: ./scripts/gstack-install.sh

set -euo pipefail

GSTACK_DIR="${HOME}/.claude/skills/gstack"

if [[ -e "$GSTACK_DIR" ]]; then
  echo "gstack already present at $GSTACK_DIR"
  echo "  To update, run: (cd $GSTACK_DIR && git pull && ./setup)"
  exit 0
fi

git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git "$GSTACK_DIR"
(cd "$GSTACK_DIR" && ./setup)
