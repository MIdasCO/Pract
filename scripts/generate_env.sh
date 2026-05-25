#!/usr/bin/env bash
set -euo pipefail

# Locate git remote URL
REMOTE_URL=""
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  REMOTE_URL=$(git remote get-url origin 2>/dev/null || git config --get remote.origin.url || true)
fi

if [ -z "$REMOTE_URL" ]; then
  echo "No git remote URL found. Please run this inside a git repo or set GIT_OWNER manually." >&2
  exit 1
fi

# Parse owner from URL formats like:
# git@github.com:owner/repo.git
# https://github.com/owner/repo.git
OWNER=$(echo "$REMOTE_URL" | sed -E 's#(.+[:/])([^/]+)/([^/]+)(\.git)?#\2#')

# Lowercase and sanitize
OWNER=$(echo "$OWNER" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9_-' '_')

echo "GIT_OWNER=$OWNER" > .env
echo ".env written with GIT_OWNER=$OWNER"
