#!/usr/bin/env python3
"""Build every artifact from the note source.

    score/piece.toml  ->  build/piece.musicxml   notation, canonical
                          build/piece.mid        sequencer / DAW
                          build/score-NNN.svg    engraved pages
                          build/performance.json input to render_audio.swift
                          build/piece.pdf        if cairosvg is installed

The note source is the ONLY place music lives. Everything under build/ is
derived and disposable. Composers edit the note source; they should never need
to edit this file in order to write music.

Usage: tools/build.py
"""
from __future__ import annotations

import json
import math
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "score" / "piece.toml"
BUILD = ROOT / "build"

# MusicXML divisions per quarter note. 24 divides cleanly by 2 and 3, so both
# duplet and triplet subdivisions land on integers.
DIV = 24

UNIT_DENOMINATOR = {"whole": 1, "half": 2, "quarter": 4, "eighth": 8,
                    "sixteenth": 16, "thirty-second": 32}
BEAT_IN_QUARTERS = {"quarter": 1.0, "dotted-quarter": 1.5, "half": 2.0,
                    "dotted-half": 3.0, "eighth": 0.5}
STEP_SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
VELOCITY = {"ppp": 35, "pp": 43, "p": 52, "mp": 62, "mf": 74, "f": 84,
            "ff": 94, "fff": 104}
CLEF = {"treble": ("G", 2), "bass": ("F", 4), "alto": ("C", 3),
        "tenor": ("C", 4), "treble8vb": ("G", 2)}

# duration in divisions -> (MusicXML type name, number of dots)
_BASE_TYPES = [("whole", 4 * DIV), ("half", 2 * DIV), ("quarter", DIV),
               ("eighth", DIV // 2), ("16th", DIV // 4), ("32nd", DIV // 8)]

TOKEN_RE = re.compile(r"^(?P<pitches>[^:]+):(?P<dur>\d+)(?P<tie>~?)$")
PITCH_RE = re.compile(r"^(?P<step>[A-G])(?P<alter>[#b]*)(?P<octave>-?\d+)$")


class SourceError(Exception):
    """A problem in the note source that the composer must fix."""


def fail(msg: str) -> None:
    raise SourceError(msg)


def note_type(duration: int) -> tuple[str, int]:
    """Map a duration in divisions onto a notated note type and dot count."""
    for name, base in _BASE_TYPES:
        for dots, factor in ((0, 1.0), (1, 1.5), (2, 1.75)):
            if abs(duration - base * factor) < 1e-9:
                return name, dots
    fail(f"duration of {duration} divisions is not a notatable note value. "
         f"Split it into two tied notes (append '~' to the first).")


def parse_pitch(text: str) -> int:
    m = PITCH_RE.match(text)
    if not m:
        fail(f"cannot read pitch {text!r}. Expected a form like A4, Bb3, F#5.")
    alter = m["alter"].count("#") - m["alter"].count("b")
    midi = 12 * (int(m["octave"]) + 1) + STEP_SEMITONES[m["step"]] + alter
    if not 0 <= midi <= 127:
        fail(f"pitch {text!r} is outside the MIDI range.")
    return midi


def parse_bar(text: str, bar_no: int, voice_id: str) -> list[dict]:
    """Parse one bar of the note source into a list of chord/rest events."""
    events = []
    for token in text.split():
        m = TOKEN_RE.match(token)
        if not m:
            fail(f"bar {bar_no}, voice {voice_id!r}: cannot read token "
                 f"{token!r}. Expected PITCH:UNITS, e.g. A4:2, or a chord "
                 f"C4,E4,G4:2, or a rest r:1, optionally tied with a "
                 f"trailing ~.")
        raw = m["pitches"]
        units = int(m["dur"])
        if units < 1:
            fail(f"bar {bar_no}, voice {voice_id!r}: {token!r} has no duration.")
        pitches = None if raw == "r" else [parse_pitch(p) for p in raw.split(",")]
        if pitches is not None and len(set(pitches)) != len(pitches):
            fail(f"bar {bar_no}, voice {voice_id!r}: {token!r} repeats a pitch "
                 f"within one chord.")
        events.append({"pitches": pitches, "units": units,
                       "tie": bool(m["tie"]), "token": token})
    return events


def load_source() -> dict:
    if not SOURCE.exists():
        fail(f"{SOURCE.relative_to(ROOT)} does not exist.")
    with SOURCE.open("rb") as fh:
        doc = tomllib.load(fh)

    settings = doc.get("settings", {})
    unit = settings.get("unit", "eighth")
    if unit not in UNIT_DENOMINATOR:
        fail(f"settings.unit {unit!r} is not one of {sorted(UNIT_DENOMINATOR)}.")
    meter = settings.get("meter", "4/4")
    try:
        beats, beat_type = (int(x) for x in meter.split("/"))
    except ValueError:
        fail(f"settings.meter {meter!r} is not of the form 4/4.")

    # Divisions per source unit, and how many units fill one bar.
    per_unit, rem = divmod(DIV * 4, UNIT_DENOMINATOR[unit])
    if rem:
        fail(f"settings.unit {unit!r} does not divide evenly into the "
             f"internal resolution; use eighth, sixteenth or quarter.")
    units_per_bar = beats * UNIT_DENOMINATOR[unit] / beat_type
    if units_per_bar != int(units_per_bar):
        fail(f"a {meter} bar is not a whole number of {unit} units. "
             f"Choose a finer settings.unit.")

    doc["_derived"] = {
        "unit": unit, "meter": meter, "beats": beats, "beat_type": beat_type,
        "per_unit": per_unit, "units_per_bar": int(units_per_bar),
    }
    return doc


def build_parts(doc: dict) -> list[dict]:
    """Parse every part and voice, validating bar lengths as we go."""
    d = doc["_derived"]
    parts = doc.get("part")
    if not parts:
        fail("the note source defines no [[part]]. At least one is required.")

    bar_counts = set()
    built = []
    for p_index, part in enumerate(parts, start=1):
        pid = part.get("id") or f"P{p_index}"
        voices = part.get("voice")
        if not voices:
            fail(f"part {pid!r} defines no [[part.voice]].")
        staves = int(part.get("staves", 1))
        built_voices = []
        for v_index, voice in enumerate(voices, start=1):
            vid = voice.get("id") or f"v{v_index}"
            staff = int(voice.get("staff", 1))
            if not 1 <= staff <= staves:
                fail(f"part {pid!r}, voice {vid!r}: staff {staff} is outside "
                     f"the {staves} stave(s) declared for the part.")
            clef = voice.get("clef", "treble")
            if clef not in CLEF:
                fail(f"part {pid!r}, voice {vid!r}: clef {clef!r} is not one "
                     f"of {sorted(CLEF)}.")
            bars = voice.get("bars")
            if bars is None:
                fail(f"part {pid!r}, voice {vid!r}: no 'bars' array.")
            parsed = []
            for bar_no, text in enumerate(bars, start=1):
                events = parse_bar(text, bar_no, vid)
                total = sum(e["units"] for e in events)
                if total != d["units_per_bar"]:
                    fail(f"part {pid!r}, voice {vid!r}, bar {bar_no}: holds "
                         f"{total} {d['unit']} units, but a {d['meter']} bar "
                         f"needs {d['units_per_bar']}. Bar reads: {text!r}")
                parsed.append(events)
            bar_counts.add(len(parsed))
            built_voices.append({"id": vid, "staff": staff, "clef": clef,
                                 "bars": parsed})

        # An instrument's range is a hard fact about the instrument, not a
        # matter of taste: a violin has no note below its open G. Catching this
        # at build time is far better than discovering it at a rehearsal.
        span = part.get("range")
        if span:
            if len(span) != 2:
                fail(f"part {pid!r}: 'range' must be two pitches, "
                     f"low and high, e.g. range = [\"G3\", \"A6\"].")
            low, high = parse_pitch(span[0]), parse_pitch(span[1])
            if low > high:
                fail(f"part {pid!r}: range low note {span[0]!r} is above the "
                     f"high note {span[1]!r}.")
            for voice in built_voices:
                for bar_no, events in enumerate(voice["bars"], start=1):
                    for event in events:
                        for pitch in event["pitches"] or ():
                            if not low <= pitch <= high:
                                where = "below" if pitch < low else "above"
                                fail(f"part {pid!r}, voice {voice['id']!r}, "
                                     f"bar {bar_no}: {event['token']!r} is "
                                     f"{where} the instrument's range "
                                     f"({span[0]}-{span[1]}).")

        built.append({"id": pid, "name": part.get("name", pid),
                      "program": int(part.get("program", 0)),
                      "staves": staves, "voices": built_voices,
                      "dynamic": part.get("dynamic")})

    if len(bar_counts) > 1:
        fail(f"voices disagree on the length of the piece: found bar counts "
             f"{sorted(bar_counts)}. Every voice must have the same number of "
             f"bars; pad short voices with rests.")
    if not bar_counts or bar_counts == {0}:
        fail("the piece has no bars yet.")
    return built


def tempo_map(doc: dict, n_bars: int) -> list[float]:
    """Quarter-notes-per-minute in force for each bar (1-indexed -> index 0)."""
    marks = doc.get("tempo") or [{"bar": 1, "bpm": 96}]
    table = {}
    for mark in marks:
        bar = int(mark.get("bar", 1))
        beat = mark.get("beat", "quarter")
        if beat not in BEAT_IN_QUARTERS:
            fail(f"tempo at bar {bar}: beat {beat!r} is not one of "
                 f"{sorted(BEAT_IN_QUARTERS)}.")
        table[bar] = float(mark["bpm"]) * BEAT_IN_QUARTERS[beat]
    if 1 not in table:
        fail("the tempo map does not say what the tempo is at bar 1.")
    out, current = [], table[1]
    for bar in range(1, n_bars + 1):
        current = table.get(bar, current)
        out.append(current)
    return out


def expand_dynamics(marks, n_bars: int, seed: str | None, where: str) -> list[str]:
    """Turn a sparse list of dynamic marks into one value per bar."""
    table = {}
    for mark in marks:
        bar, name = int(mark.get("bar", 1)), mark["mark"]
        if name not in VELOCITY:
            fail(f"{where}, dynamic at bar {bar}: {name!r} is not one of "
                 f"{sorted(VELOCITY, key=VELOCITY.get)}.")
        table[bar] = name
    current = table.get(1, seed)
    if current is None:
        fail(f"{where}: the dynamic map does not say how loud bar 1 is.")
    out = []
    for bar in range(1, n_bars + 1):
        current = table.get(bar, current)
        out.append(current)
    return out


def dynamic_map(doc: dict, n_bars: int) -> list[str]:
    return expand_dynamics(doc.get("dynamic") or [{"bar": 1, "mark": "mf"}],
                           n_bars, None, "the score")


def dynamics_per_part(parts, base: list[str], n_bars: int) -> list[list[str]]:
    """Each part follows the score's dynamics unless it gives its own.

    Chamber music lives on the balance between players, so any part may set
    its own line independently — a cello can sit under the violins.
    """
    return [expand_dynamics(part["dynamic"], n_bars, base[0],
                            f"part {part['id']!r}")
            if part["dynamic"] else base
            for part in parts]


def flatten(part: dict, per_unit: int, units_per_bar: int) -> list[dict]:
    """Resolve one part's voices into absolute-division note events.

    Ties are merged here, so a tied pair becomes a single sounding note.
    """
    notes = []
    bar_divs = units_per_bar * per_unit
    for voice in part["voices"]:
        pending = {}          # pitch -> index into notes, awaiting a tie stop
        for bar_index, events in enumerate(voice["bars"]):
            cursor = bar_index * bar_divs
            for event in events:
                dur = event["units"] * per_unit
                if event["pitches"] is None:
                    if pending:
                        fail(f"voice {voice['id']!r}, bar {bar_index + 1}: a "
                             f"tie runs into a rest. Ties must join two notes "
                             f"of the same pitch.")
                    cursor += dur
                    continue
                for pitch in event["pitches"]:
                    if pitch in pending:
                        notes[pending.pop(pitch)]["duration"] += dur
                    else:
                        notes.append({"pitch": pitch, "start": cursor,
                                      "duration": dur, "voice": voice["id"],
                                      "staff": voice["staff"],
                                      "bar": bar_index + 1})
                if event["tie"]:
                    for pitch in event["pitches"]:
                        # index of the note just written or extended
                        for i in range(len(notes) - 1, -1, -1):
                            if notes[i]["pitch"] == pitch and \
                               notes[i]["voice"] == voice["id"]:
                                pending[pitch] = i
                                break
                cursor += dur
        if pending:
            fail(f"voice {voice['id']!r}: a tie at the end of the piece is "
                 f"never resolved. Remove the trailing '~'.")
    return notes


KEY_FIFTHS = {"C": 0, "Am": 0, "G": 1, "Em": 1, "D": 2, "Bm": 2, "A": 3,
              "F#m": 3, "E": 4, "C#m": 4, "B": 5, "G#m": 5, "F#": 6,
              "D#m": 6, "F": -1, "Dm": -1, "Bb": -2, "Gm": -2, "Eb": -3,
              "Cm": -3, "Ab": -4, "Fm": -4, "Db": -5, "Bbm": -5,
              "Gb": -6, "Ebm": -6}
# Preferred spelling per key signature: True = sharps, False = flats.
SHARP_KEYS = {k for k, v in KEY_FIFTHS.items() if v > 0}
NAMES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NAMES_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]


def spell(midi: int, use_sharps: bool) -> tuple[str, int, int]:
    """MIDI number -> (step, alter, octave) using the key's preferred spelling."""
    name = (NAMES_SHARP if use_sharps else NAMES_FLAT)[midi % 12]
    octave = midi // 12 - 1
    alter = 1 if "#" in name else (-1 if "b" in name else 0)
    return name[0], alter, octave


def esc(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def emit_musicxml(doc, parts, tempi, dyn_by_part) -> str:
    d = doc["_derived"]
    meta = doc.get("meta", {})
    key = doc.get("settings", {}).get("key", "C")
    if key not in KEY_FIFTHS:
        fail(f"settings.key {key!r} is not a key I can notate. "
             f"Known: {', '.join(sorted(KEY_FIFTHS))}")
    use_sharps = key in SHARP_KEYS
    words = {int(k): v for k, v in (doc.get("marks") or {}).items()}
    n_bars = len(parts[0]["voices"][0]["bars"])
    bar_divs = d["units_per_bar"] * d["per_unit"]

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<!DOCTYPE score-partwise PUBLIC '
           '"-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
           '"http://www.musicxml.org/dtds/partwise.dtd">',
           '<score-partwise version="4.0">',
           f'  <work><work-title>{esc(meta.get("title", "Untitled"))}'
           f'</work-title></work>',
           '  <identification>',
           f'    <creator type="composer">'
           f'{esc(", ".join(meta.get("composers", [])))}</creator>',
           '    <encoding><software>AIMusicComposer tools/build.py</software>'
           '</encoding>',
           '  </identification>',
           '  <part-list>']
    for i, part in enumerate(parts, start=1):
        out += [f'    <score-part id="P{i}">',
                f'      <part-name>{esc(part["name"])}</part-name>',
                f'      <score-instrument id="P{i}-I1"><instrument-name>'
                f'{esc(part["name"])}</instrument-name></score-instrument>',
                f'      <midi-instrument id="P{i}-I1"><midi-channel>{i}'
                f'</midi-channel><midi-program>{part["program"] + 1}'
                f'</midi-program></midi-instrument>',
                '    </score-part>']
    out.append('  </part-list>')

    for i, part in enumerate(parts, start=1):
        out.append(f'  <part id="P{i}">')
        for bar in range(1, n_bars + 1):
            out.append(f'    <measure number="{bar}">')
            if bar == 1:
                out += ['      <attributes>',
                        f'        <divisions>{DIV}</divisions>',
                        f'        <key><fifths>{KEY_FIFTHS[key]}</fifths></key>',
                        f'        <time><beats>{d["beats"]}</beats>'
                        f'<beat-type>{d["beat_type"]}</beat-type></time>',
                        f'        <staves>{part["staves"]}</staves>']
                seen = {}
                for voice in part["voices"]:
                    seen.setdefault(voice["staff"], voice["clef"])
                for staff in range(1, part["staves"] + 1):
                    sign, line = CLEF[seen.get(staff, "treble")]
                    out.append(f'        <clef number="{staff}"><sign>{sign}'
                               f'</sign><line>{line}</line></clef>')
                out.append('      </attributes>')
            # Tempo and expression marks head the score, so they go on the
            # top part only. Dynamics belong to each player and are printed
            # under every part that has them.
            if i == 1:
                if bar == 1 or tempi[bar - 1] != tempi[bar - 2]:
                    out += ['      <direction placement="above">',
                            '        <direction-type><metronome>'
                            '<beat-unit>quarter</beat-unit>'
                            f'<per-minute>{round(tempi[bar - 1])}</per-minute>'
                            '</metronome></direction-type>',
                            '      </direction>']
                if bar in words:
                    out += ['      <direction placement="above">',
                            '        <direction-type><words>'
                            f'{esc(words[bar])}</words></direction-type>',
                            '      </direction>']
            dynamics = dyn_by_part[i - 1]
            if bar == 1 or dynamics[bar - 1] != dynamics[bar - 2]:
                out += ['      <direction placement="below">',
                        '        <direction-type><dynamics>'
                        f'<{dynamics[bar - 1]}/></dynamics></direction-type>',
                        '      </direction>']
            for v_index, voice in enumerate(part["voices"]):
                if v_index:
                    out.append(f'      <backup><duration>{bar_divs}'
                               f'</duration></backup>')
                pending = set()
                for event in voice["bars"][bar - 1]:
                    dur = event["units"] * d["per_unit"]
                    type_name, dots = note_type(dur)
                    if event["pitches"] is None:
                        out += ['      <note>', '        <rest/>',
                                f'        <duration>{dur}</duration>',
                                f'        <voice>{v_index + 1}</voice>',
                                f'        <type>{type_name}</type>',
                                *['        <dot/>'] * dots,
                                f'        <staff>{voice["staff"]}</staff>',
                                '      </note>']
                        continue
                    for n, pitch in enumerate(event["pitches"]):
                        step, alter, octave = spell(pitch, use_sharps)
                        stops = pitch in pending
                        ties = []
                        if stops:
                            ties.append('        <tie type="stop"/>')
                        if event["tie"]:
                            ties.append('        <tie type="start"/>')
                        notations = []
                        if stops:
                            notations.append('<tied type="stop"/>')
                        if event["tie"]:
                            notations.append('<tied type="start"/>')
                        out.append('      <note>')
                        if n:
                            out.append('        <chord/>')
                        out += ['        <pitch>',
                                f'          <step>{step}</step>',
                                *([f'          <alter>{alter}</alter>']
                                  if alter else []),
                                f'          <octave>{octave}</octave>',
                                '        </pitch>',
                                f'        <duration>{dur}</duration>',
                                *ties,
                                f'        <voice>{v_index + 1}</voice>',
                                f'        <type>{type_name}</type>',
                                *['        <dot/>'] * dots,
                                f'        <staff>{voice["staff"]}</staff>']
                        if notations:
                            out.append('        <notations>'
                                       + "".join(notations) + '</notations>')
                        out.append('      </note>')
                    pending = set(event["pitches"]) if event["tie"] else set()
            out.append('    </measure>')
        out.append('  </part>')
    out.append('</score-partwise>')
    return "\n".join(out) + "\n"


def bar_start_seconds(tempi, bar_divs, n_bars) -> list[float]:
    starts, clock = [], 0.0
    for bar in range(n_bars):
        starts.append(clock)
        clock += bar_divs * 60.0 / (tempi[bar] * DIV)
    starts.append(clock)
    return starts


def emit_midi(doc, parts, tempi, dyn_by_part, path: Path) -> None:
    import mido
    d = doc["_derived"]
    bar_divs = d["units_per_bar"] * d["per_unit"]
    n_bars = len(parts[0]["voices"][0]["bars"])

    midi = mido.MidiFile(ticks_per_beat=DIV)
    conductor = mido.MidiTrack()
    conductor.append(mido.MetaMessage(
        "track_name", name=doc.get("meta", {}).get("title", "Untitled"), time=0))
    events = []
    for bar in range(n_bars):
        if bar == 0 or tempi[bar] != tempi[bar - 1]:
            events.append((bar * bar_divs, mido.MetaMessage(
                "set_tempo", tempo=int(round(60_000_000 / tempi[bar])))))
    events.append((n_bars * bar_divs, mido.MetaMessage("end_of_track")))
    clock = 0
    for when, message in events:
        message.time = when - clock
        clock = when
        conductor.append(message)
    midi.tracks.append(conductor)

    for channel, part in enumerate(parts):
        dynamics = dyn_by_part[channel]
        track = mido.MidiTrack()
        track.append(mido.MetaMessage("track_name", name=part["name"], time=0))
        track.append(mido.Message("program_change", channel=channel,
                                  program=part["program"], time=0))
        raw = []
        for note in flatten(part, d["per_unit"], d["units_per_bar"]):
            velocity = VELOCITY[dynamics[note["bar"] - 1]]
            raw.append((note["start"], 1, mido.Message(
                "note_on", channel=channel, note=note["pitch"],
                velocity=velocity, time=0)))
            raw.append((note["start"] + note["duration"], 0, mido.Message(
                "note_off", channel=channel, note=note["pitch"],
                velocity=0, time=0)))
        # note_off sorts before note_on at the same tick, so a repeated pitch
        # is released before it is struck again.
        raw.sort(key=lambda item: (item[0], item[1]))
        clock = 0
        for when, _, message in raw:
            message.time = when - clock
            clock = when
            track.append(message)
        midi.tracks.append(track)
    midi.save(str(path))


def emit_performance(doc, parts, tempi, dyn_by_part) -> dict:
    """Absolute-time events for tools/render_audio.swift."""
    d = doc["_derived"]
    bar_divs = d["units_per_bar"] * d["per_unit"]
    n_bars = len(parts[0]["voices"][0]["bars"])
    starts = bar_start_seconds(tempi, bar_divs, n_bars)

    def seconds(position: int) -> float:
        bar = min(position // bar_divs, n_bars - 1)
        offset = position - bar * bar_divs
        return starts[bar] + offset * 60.0 / (tempi[bar] * DIV)

    events = []
    for channel, part in enumerate(parts):
        dynamics = dyn_by_part[channel]
        for note in flatten(part, d["per_unit"], d["units_per_bar"]):
            velocity = VELOCITY[dynamics[note["bar"] - 1]]
            on = seconds(note["start"])
            off = seconds(note["start"] + note["duration"])
            # Release fractionally early so repeated notes re-articulate.
            off = max(on + 0.02, off - 0.02)
            events.append({"time": round(on, 6), "type": "on",
                           "channel": channel, "note": note["pitch"],
                           "velocity": velocity})
            events.append({"time": round(off, 6), "type": "off",
                           "channel": channel, "note": note["pitch"]})
    for pedal in doc.get("pedal") or []:
        bar = int(pedal["bar"])
        if not 1 <= bar <= n_bars:
            fail(f"pedal mark at bar {bar} is outside the piece "
                 f"(1-{n_bars}).")
        events.append({"time": round(starts[bar - 1], 6), "type": "pedal",
                       "channel": int(pedal.get("part", 1)) - 1,
                       "value": 127 if pedal.get("down", True) else 0})
    events.sort(key=lambda e: (e["time"], e["type"] != "off"))
    tail = float(doc.get("settings", {}).get("release_seconds", 4.0))
    # The renderer needs one instrument per channel: a single sampler is
    # monotimbral, so without this every part would come out as a piano.
    voices = [{"channel": i, "name": part["name"], "program": part["program"]}
              for i, part in enumerate(parts)]
    return {"duration": round(starts[n_bars] + tail, 6),
            "parts": voices, "events": events}


def engrave(musicxml: str) -> int:
    import verovio
    toolkit = verovio.toolkit()
    toolkit.setOptions({"pageWidth": 2100, "pageHeight": 2970, "scale": 40,
                        "adjustPageHeight": False, "footer": "auto",
                        "header": "auto"})
    if not toolkit.loadData(musicxml):
        fail("verovio could not load the generated MusicXML. This is a bug in "
             "tools/build.py, not in your music - please report it.")
    pages = toolkit.getPageCount()
    for page in range(1, pages + 1):
        (BUILD / f"score-{page:03d}.svg").write_text(
            toolkit.renderToSVG(page), encoding="utf-8")
    return pages


def main() -> int:
    try:
        doc = load_source()
        parts = build_parts(doc)
        d = doc["_derived"]
        n_bars = len(parts[0]["voices"][0]["bars"])
        tempi = tempo_map(doc, n_bars)
        dyn_by_part = dynamics_per_part(parts, dynamic_map(doc, n_bars), n_bars)

        BUILD.mkdir(exist_ok=True)
        for stale in BUILD.glob("score-*.svg"):
            stale.unlink()

        musicxml = emit_musicxml(doc, parts, tempi, dyn_by_part)
        (BUILD / "piece.musicxml").write_text(musicxml, encoding="utf-8")
        emit_midi(doc, parts, tempi, dyn_by_part, BUILD / "piece.mid")
        performance = emit_performance(doc, parts, tempi, dyn_by_part)
        (BUILD / "performance.json").write_text(
            json.dumps(performance, indent=1), encoding="utf-8")
        pages = engrave(musicxml)
    except SourceError as error:
        print(f"BUILD FAILED\n  {error}", file=sys.stderr)
        return 1

    notes = sum(1 for e in performance["events"] if e["type"] == "on")
    print(f"Built {n_bars} bars, {len(parts)} part(s), {notes} notes, "
          f"{performance['duration']:.1f}s")
    print("  build/piece.musicxml   notation (open in MuseScore, Finale, ...)")
    print("  build/piece.mid        MIDI")
    print(f"  build/score-*.svg      engraved score, {pages} page(s)")
    print("  build/performance.json input to tools/render_audio.swift")
    return 0


if __name__ == "__main__":
    sys.exit(main())
