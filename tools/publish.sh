#!/usr/bin/env bash
# Publish this repository to a NEW PUBLIC repository on GitHub.
#
# This is deliberately a manual step. Running it makes the work public and
# is not easily undone, so no composing turn should ever invoke it. A human
# runs this, once, when the piece is ready to be seen.
#
# Usage: tools/publish.sh <github-user>/<repo-name>
set -euo pipefail
cd "$(dirname "$0")/.."

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
  echo "Usage: tools/publish.sh <github-user>/<repo-name>"
  echo "Example: tools/publish.sh samharden/ai-music-composer"
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  cat <<'MSG'
The GitHub CLI ('gh') is not installed, so this script cannot create the
repository for you. Two options:

  A. Install it, then re-run this script:
       brew install gh
       gh auth login

  B. Do it by hand:
       1. Create an empty PUBLIC repo on github.com (no README, no license,
          no .gitignore — this repo already has them).
       2. Then run:
            git remote add origin git@github.com:<user>/<repo>.git
            git push -u origin main
MSG
  exit 1
fi

echo "About to create a PUBLIC repository: $TARGET"
echo "Everything committed here becomes visible to anyone on the internet."
printf 'Type the repo name again to confirm: '
read -r confirm
if [ "$confirm" != "$TARGET" ]; then
  echo "Names did not match. Nothing was published."
  exit 1
fi

./tools/check.sh || { echo "Score does not pass checks. Fix it before publishing."; exit 1; }

gh repo create "$TARGET" --public --source=. --remote=origin --push
echo
echo "Published: https://github.com/$TARGET"
