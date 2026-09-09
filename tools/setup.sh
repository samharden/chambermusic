#!/usr/bin/env bash
# One-time setup: create the virtual environment and install dependencies.
# Usage: tools/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."

command -v python3 >/dev/null || { echo "python3 is required."; exit 1; }
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt
echo "Environment ready."

if command -v swift >/dev/null 2>&1; then
  echo "swift found: audio rendering is available."
else
  echo "NOTE: 'swift' is not installed, so tools/render.sh cannot produce"
  echo "      audio. Notation and MIDI still build. Install Xcode command"
  echo "      line tools with: xcode-select --install"
fi
