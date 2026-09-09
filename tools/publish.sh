#!/usr/bin/env bash
# Push this repository to its public home on GitHub.
#
# This is deliberately a manual step. Pushing makes the work visible to anyone
# on the internet and is not easily undone, so no composing turn should ever
# invoke it. A human runs this when the work is ready to be seen.
#
# Usage: tools/publish.sh
set -euo pipefail
cd "$(dirname "$0")/.."

REMOTE="${1:-origin}"

if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  echo "No git remote named '$REMOTE'. Add one with:"
  echo "  git remote add origin git@github.com:<user>/<repo>.git"
  exit 1
fi
URL="$(git remote get-url "$REMOTE")"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ -n "$(git status --porcelain)" ]; then
  echo "The working tree has uncommitted changes. Commit them first:"
  git status --short
  exit 1
fi

./tools/check.sh || {
  echo "The score does not pass its checks. Fix it before publishing."
  exit 1
}

git fetch --quiet "$REMOTE" "$BRANCH" 2>/dev/null || true
AHEAD="$(git rev-list --count "$REMOTE/$BRANCH..$BRANCH" 2>/dev/null || echo "?")"
BEHIND="$(git rev-list --count "$BRANCH..$REMOTE/$BRANCH" 2>/dev/null || echo 0)"

if [ "$BEHIND" != "0" ]; then
  echo "The remote has $BEHIND commit(s) you do not have. Pull and reconcile"
  echo "before publishing, so nothing is overwritten:"
  echo "  git pull --rebase $REMOTE $BRANCH"
  exit 1
fi
if [ "$AHEAD" = "0" ]; then
  echo "Nothing to publish: $REMOTE/$BRANCH already matches $BRANCH."
  exit 0
fi

echo "About to push $AHEAD commit(s) on '$BRANCH' to a PUBLIC repository:"
echo "  $URL"
git log --oneline "$REMOTE/$BRANCH..$BRANCH" | sed 's/^/    /'
echo
printf "Type 'publish' to confirm: "
read -r confirm
[ "$confirm" = "publish" ] || { echo "Nothing was pushed."; exit 1; }

git push "$REMOTE" "$BRANCH"
echo
echo "Published: ${URL%.git}"
