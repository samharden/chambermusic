#!/usr/bin/env bash
# Build everything, including audio, and verify all of it.
# Usage: tools/render.sh
set -uo pipefail
cd "$(dirname "$0")/.."

PY=".venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo "No Python found. Run tools/setup.sh."; exit 1; }

"$PY" tools/build.py || exit 1

if command -v swift >/dev/null 2>&1; then
  swift tools/render_audio.swift build/performance.json build/piece.wav \
    2>/dev/null || { echo "Audio rendering failed."; exit 1; }
  echo "  build/piece.wav        audio"
  "$PY" tools/verify.py || exit 1
else
  echo "  (no swift: skipping audio)"
  "$PY" tools/verify.py --no-audio || exit 1
fi
echo "Verified. Report written to build/verification.json"
