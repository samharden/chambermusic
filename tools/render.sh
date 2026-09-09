#!/usr/bin/env bash
# Build everything, including audio, and verify all of it.
# Usage: tools/render.sh [piece]     (no argument renders every piece)
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
  if command -v swift >/dev/null 2>&1; then
    if swift tools/render_audio.swift "pieces/$piece/build/performance.json" \
         "pieces/$piece/build/piece.wav" 2>/dev/null; then
      echo "  pieces/$piece/build/piece.wav        audio"
      "$PY" tools/verify.py "$piece" || failed=1
    else
      echo "Audio rendering failed for $piece."
      failed=1
    fi
  else
    echo "  (no swift: skipping audio)"
    "$PY" tools/verify.py "$piece" --no-audio || failed=1
  fi
done
exit "$failed"
