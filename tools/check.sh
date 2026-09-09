#!/usr/bin/env bash
# The gate every turn must pass. Fast: no audio rendering.
#
#   - the note source parses, and every bar is metrically complete
#   - notation and MIDI are generated
#   - the two agree, note for note, independently re-derived
#
# Usage: tools/check.sh [piece]     (no argument checks every piece)
set -uo pipefail
cd "$(dirname "$0")/.."

PY=".venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo "No Python found. Run tools/setup.sh."; exit 1; }

if [ $# -gt 0 ]; then
  PIECES=("$@")
else
  PIECES=()
  for dir in pieces/*/; do
    [ -f "$dir/score/piece.toml" ] && PIECES+=("$(basename "$dir")")
  done
fi
[ ${#PIECES[@]} -gt 0 ] || { echo "No pieces found under pieces/."; exit 1; }

failed=0
for piece in "${PIECES[@]}"; do
  "$PY" tools/build.py "$piece" || { failed=1; continue; }
  "$PY" tools/verify.py "$piece" --no-audio >/dev/null || failed=1
done

if [ "$failed" -eq 0 ]; then
  echo "OK: every score builds and its notation matches its MIDI."
fi
exit "$failed"
