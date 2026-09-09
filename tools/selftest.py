#!/usr/bin/env python3
"""Prove the audio renderer actually mixes every instrument.

The failure this guards against is silent and total: wiring several players
into a node that has only one input bus keeps the last connection and drops
everyone else. The audio still renders, still passes every loudness and
duration check, and contains one instrument instead of five.

The test asks the question directly, once per part: render the full ensemble,
then render it again with that one player removed. If the player is reaching
the mix, the two renders must differ. If it is being dropped, they are
identical.

(An earlier version compared the mix against the sum of the parts rendered
alone. That assumes the signal path is linear, and the reverb is not quite -
five separate reverb instances are not the same as one reverb on the sum - so
it reported a few percent of error on music that was perfectly fine.)

Usage: tools/selftest.py <piece>
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RENDERER = ROOT / "tools" / "render_audio.swift"


def render(spec: dict, out: Path, work: Path) -> np.ndarray:
    path = work / (out.stem + ".json")
    path.write_text(json.dumps(spec))
    result = subprocess.run(["swift", str(RENDERER), str(path), str(out)],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(f"renderer failed for {out.name}")
    with wave.open(str(out), "rb") as handle:
        frames = handle.readframes(handle.getnframes())
    return np.frombuffer(frames, dtype="<i2").astype(np.float64) / 32768.0


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if len(args) != 1:
        raise SystemExit("Usage: tools/selftest.py <piece>")
    performance_path = ROOT / "pieces" / args[0] / "build" / "performance.json"
    if not performance_path.exists():
        print(f"{performance_path} is missing. Run tools/build.py first.",
              file=sys.stderr)
        return 1
    performance = json.loads(performance_path.read_text())
    parts = performance.get("parts") or []
    if len(parts) < 2:
        print(f"Only {len(parts)} part(s); the mixing test needs at least 2. "
              f"Skipped.")
        return 0
    sounding = {e["channel"] for e in performance["events"] if e["type"] == "on"}
    if len(sounding) < 2:
        print(f"Only {len(sounding)} part(s) actually play; the mixing test "
              f"needs at least 2. Skipped — write some music first.")
        return 0

    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        full = render(performance, work / "full.wav", work)
        reference = np.sqrt(np.mean(full ** 2))
        if reference <= 0:
            print("The full mix is silent.", file=sys.stderr)
            return 1

        for part in parts:
            channel = part["channel"]
            events = [e for e in performance["events"]
                      if e["channel"] == channel]
            if not any(e["type"] == "on" for e in events):
                print(f"  {part['name']:<12} rests throughout, skipped")
                continue

            # Alone: does this instrument make a sound at all?
            solo = dict(performance, parts=[part], events=events)
            alone = render(solo, work / f"solo{channel}.wav", work)
            peak = np.abs(alone).max()
            if peak < 0.001:
                failures.append(f"{part['name']} renders no audible sound")

            # Removed: does taking it away change the ensemble?
            rest = dict(performance,
                        parts=[q for q in parts if q["channel"] != channel],
                        events=[e for e in performance["events"]
                                if e["channel"] != channel])
            without = render(rest, work / f"without{channel}.wav", work)
            n = min(len(full), len(without))
            contribution = (np.sqrt(np.mean((full[:n] - without[:n]) ** 2))
                            / reference)
            print(f"  {part['name']:<12} program {part['program']:<3} "
                  f"alone {20 * np.log10(peak):6.2f} dBFS   "
                  f"contributes {contribution * 100:5.1f}% of the mix")
            if contribution < 0.01:
                failures.append(
                    f"{part['name']} changes nothing when removed from the "
                    f"mix - it is not reaching the output")

    if failures:
        print("\nSELFTEST FAILED", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print("\nOK: every part is audible and all of them reach the mix.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
