#!/usr/bin/env bash
# The gate every turn must pass. Fast: no audio rendering.
#
#   - the note source parses, and every bar is metrically complete
#   - notation and MIDI are generated
#   - the two agree, note for note, independently re-derived
#
# Usage: tools/check.sh
set -uo pipefail
cd "$(dirname "$0")/.."

PY=".venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo "No Python found. Run tools/setup.sh."; exit 1; }

"$PY" tools/build.py  || exit 1
"$PY" tools/verify.py --no-audio >/dev/null || exit 1
echo "OK: the score builds and the notation matches the MIDI."
