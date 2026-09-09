# AIMusicComposer

Two AI models composing one piece of music, in the open, one turn at a time.

**GPT-6 Astra** and **Fable 5.1** take alternating turns on a single score.
Each turn is a git commit: some music, and a note explaining what it was
answering and what it is leaving for the other composer. The commit history is
the point as much as the piece is — it is a record of two models trying to
write something together, including the disagreements.

## What is in here

| Path | |
|---|---|
| `score/piece.toml` | **The composition.** Plain text. The only place music lives. |
| `brief/BRIEF.md` | The constraints both composers work within |
| `log/TURNS.md` | The turn ledger — whose turn it is, and what each turn did |
| `log/turns/` | One note per turn: intent, reasoning, what was left open |
| `tools/` | Build, check, render, verify, publish |
| `build/` | Generated output. Disposable, gitignored, never edited by hand. |

## Quickstart

```bash
tools/setup.sh     # once: virtualenv and dependencies
tools/render.sh    # build everything and verify it
```

That produces, in `build/`:

- `piece.musicxml` — notation, openable in MuseScore, Finale, Dorico, Sibelius
- `score-001.svg` … — the engraved score, one file per page
- `piece.mid` — MIDI
- `piece.wav` — audio
- `verification.json` — proof the three agree

While composing, `tools/check.sh` is the fast gate: it builds and confirms the
notation and MIDI match, without rendering audio.

## How the music is written

The score is plain text, so a musical change shows up as a musical diff:

```toml
[[part.voice]]
id = "rh"
staff = 1
clef = "treble"
bars = [
  "A4:2 D5:1 C5:2 A4:2",     # pitch:units — one bar per line
  "F4,A4,C5:4 r:4",          # a chord, then a rest
  "G4:6~ G4:2",              # a tie: one sounding note of 8 units
]
```

`tools/build.py` turns that into notation, MIDI and a performance, and
`tools/verify.py` independently re-derives the notes from the generated
notation and checks that all three agree — so a bug in the build shows up as a
failed check rather than as a quietly wrong recording.

## Requirements

- **Python 3.11+** — `verovio` (engraving), `mido` (MIDI), `numpy` (audio checks)
- **Swift**, for audio only. The renderer uses the sound bank that ships with
  macOS, so there is no soundfont to install. Without Swift, everything except
  `piece.wav` still builds.

## For the composers

Read [CONTRIBUTING.md](CONTRIBUTING.md) — the relay protocol — before taking a
turn. In short: check the ledger that it is your turn, read the brief and the
last two turn notes, make one bounded change, leave `tools/check.sh` passing,
write a turn note, commit, and stop.

## Publishing

`tools/publish.sh <user>/<repo>` creates the public GitHub repository. It is a
deliberate, human-run step. Composers never run it.

## License

Code in `tools/` is MIT. The composition — `score/`, `build/` output, and
anything in `release/` — is CC BY 4.0. See [LICENSE](LICENSE).
