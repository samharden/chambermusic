#!/usr/bin/env python3
"""Check that the notation, the MIDI, and the audio all agree.

This deliberately re-derives the note events from build/piece.musicxml rather
than reusing anything in build.py. Two independent readings that agree is
evidence; one reading agreeing with itself is not. If build.py ever drops a
tie, misplaces a voice, or writes a chord to the wrong staff, the comparison
here is what catches it.

Usage: tools/verify.py [--no-audio]
"""
from __future__ import annotations

import json
import sys
import wave
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
STEP_SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

problems: list[str] = []


def check(condition: bool, message: str) -> bool:
    if not condition:
        problems.append(message)
    return condition


def read_musicxml(path: Path):
    """Re-derive (part, onset, pitch, duration) events, merging tied notes."""
    root = ET.parse(path).getroot()
    divisions = int(root.find(".//divisions").text)
    time = root.find(".//time")
    beats, beat_type = int(time.find("beats").text), int(time.find("beat-type").text)
    bar_divs = round(beats * divisions * 4 / beat_type)

    events, bar_count = [], None
    for part_index, part in enumerate(root.findall("part")):
        measures = part.findall("measure")
        if bar_count is None:
            bar_count = len(measures)
        check(len(measures) == bar_count,
              f"part {part_index + 1} has {len(measures)} bars, but part 1 "
              f"has {bar_count}")
        open_ties: dict[tuple, int] = {}
        for bar_index, measure in enumerate(measures):
            cursor = last_start = 0
            voice_totals: Counter = Counter()
            for child in measure:
                if child.tag == "backup":
                    cursor -= int(child.findtext("duration"))
                    continue
                if child.tag == "forward":
                    cursor += int(child.findtext("duration"))
                    continue
                if child.tag != "note":
                    continue
                duration = int(child.findtext("duration"))
                voice = child.findtext("voice", "1")
                is_chord = child.find("chord") is not None
                start = last_start if is_chord else cursor
                if not is_chord:
                    last_start = cursor
                    cursor += duration
                    voice_totals[voice] += duration
                pitch_el = child.find("pitch")
                if pitch_el is None:
                    continue
                midi = (12 * (int(pitch_el.findtext("octave")) + 1)
                        + STEP_SEMITONES[pitch_el.findtext("step")]
                        + int(pitch_el.findtext("alter", "0") or 0))
                check(0 <= midi <= 127,
                      f"bar {bar_index + 1}: pitch {midi} is out of MIDI range")
                onset = bar_index * bar_divs + start
                tie_types = {t.get("type") for t in child.findall("tie")}
                key = (part_index, voice, midi)
                if "stop" in tie_types and key in open_ties:
                    events[open_ties.pop(key)][3] += duration
                else:
                    events.append([part_index, onset, midi, duration])
                    if "stop" in tie_types:
                        problems.append(
                            f"bar {bar_index + 1}: a note ends a tie that no "
                            f"earlier note starts")
                if "start" in tie_types:
                    open_ties[key] = len(events) - 1 if "stop" not in tie_types \
                        else open_ties.get(key, len(events) - 1)
                    # Point at the note just written or extended.
                    for i in range(len(events) - 1, -1, -1):
                        if (events[i][0], events[i][2]) == (part_index, midi):
                            open_ties[key] = i
                            break
            for voice, total in voice_totals.items():
                check(total == bar_divs,
                      f"part {part_index + 1}, voice {voice}, bar "
                      f"{bar_index + 1}: fills {total} divisions, expected "
                      f"{bar_divs}")
        check(not open_ties,
              f"part {part_index + 1}: {len(open_ties)} tie(s) never resolve")
    return [tuple(e) for e in events], bar_count, divisions


def read_midi(path: Path):
    import mido
    midi = mido.MidiFile(str(path))
    events = []
    for track in midi.tracks:
        tick, sounding = 0, {}
        for message in track:
            tick += message.time
            if message.type == "note_on" and message.velocity:
                check((message.channel, message.note) not in sounding,
                      f"MIDI: note {message.note} is struck again while "
                      f"already sounding on channel {message.channel}")
                sounding[message.channel, message.note] = tick
            elif message.type == "note_off" or (
                    message.type == "note_on" and not message.velocity):
                start = sounding.pop((message.channel, message.note), None)
                if start is None:
                    problems.append(f"MIDI: note {message.note} is released "
                                    f"without being struck")
                    continue
                events.append((message.channel, start, message.note,
                               tick - start))
        check(not sounding, "MIDI: some notes are never released")
    return events, midi.length


def check_audio(path: Path, midi_seconds: float, release: float):
    import numpy as np
    with wave.open(str(path), "rb") as handle:
        check(handle.getnchannels() == 2, "audio is not stereo")
        check(handle.getsampwidth() == 2, "audio is not 16-bit")
        check(handle.getframerate() == 44100, "audio is not 44.1 kHz")
        frames = handle.getnframes()
        seconds = frames / handle.getframerate()
        samples = (np.frombuffer(handle.readframes(frames), dtype="<i2")
                   .astype(np.float32) / 32768.0)
    check(abs(seconds - (midi_seconds + release)) < 0.05,
          f"audio is {seconds:.2f}s but the MIDI plus its {release}s release "
          f"is {midi_seconds + release:.2f}s")
    peak = float(np.max(np.abs(samples))) if samples.size else 0.0
    rms = float(np.sqrt(np.mean(samples ** 2))) if samples.size else 0.0
    check(peak < 0.999, "audio is clipping")
    check(peak > 0.02, "audio is silent or nearly so")
    check(rms > 0.005, "audio is far too quiet to be a real performance")
    return seconds, peak, rms


def main() -> int:
    with_audio = "--no-audio" not in sys.argv
    musicxml, midi_path = BUILD / "piece.musicxml", BUILD / "piece.mid"
    for path in (musicxml, midi_path):
        if not path.exists():
            print(f"VERIFY FAILED\n  {path.relative_to(ROOT)} is missing. "
                  f"Run tools/build.py first.", file=sys.stderr)
            return 1

    score_events, bars, divisions = read_musicxml(musicxml)
    midi_events, midi_seconds = read_midi(midi_path)

    if Counter(score_events) != Counter(midi_events):
        only_score = Counter(score_events) - Counter(midi_events)
        only_midi = Counter(midi_events) - Counter(score_events)
        problems.append(
            f"the notation and the MIDI disagree: {sum(only_score.values())} "
            f"note(s) only in the score, {sum(only_midi.values())} only in "
            f"the MIDI")
        for part, onset, pitch, duration in list(only_score)[:5]:
            problems.append(f"    score only: bar "
                            f"{onset // (divisions * 4) + 1}, pitch {pitch}")
        for part, onset, pitch, duration in list(only_midi)[:5]:
            problems.append(f"    MIDI only:  bar "
                            f"{onset // (divisions * 4) + 1}, pitch {pitch}")

    report = {
        "result": "failed" if problems else "passed",
        "bars": bars,
        "note_events": len(score_events),
        "notation_matches_midi": not problems or "disagree" not in " ".join(problems),
        "midi_seconds": round(midi_seconds, 3),
    }

    wav = BUILD / "piece.wav"
    if with_audio:
        if wav.exists():
            source = ROOT / "score" / "piece.toml"
            release = 4.0
            try:
                import tomllib
                with source.open("rb") as fh:
                    release = float(tomllib.load(fh).get("settings", {})
                                    .get("release_seconds", 4.0))
            except Exception:
                pass
            seconds, peak, rms = check_audio(wav, midi_seconds, release)
            import math
            report |= {
                "audio_seconds": round(seconds, 3),
                "audio_peak_dbfs": round(20 * math.log10(peak), 2) if peak else None,
                "audio_rms_dbfs": round(20 * math.log10(rms), 2) if rms else None,
            }
        else:
            problems.append("build/piece.wav is missing. Run tools/render.sh, "
                            "or pass --no-audio to skip the audio checks.")

    report["result"] = "failed" if problems else "passed"
    BUILD.mkdir(exist_ok=True)
    (BUILD / "verification.json").write_text(json.dumps(report, indent=2))

    if problems:
        print("VERIFY FAILED", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
