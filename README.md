# chambermusic

Two AI models composing chamber music — **piano quintets** — in the open, one
turn at a time.

There are **two pieces**, written from the same brief by the same pair of
composers. The only thing that differs is who takes the first turn. Whoever
moves first states the material everything else has to answer, so the pair is
a controlled comparison: same constraints, same players, different opening
move.

**GPT-6 Astra** and **Fable 5.1** take alternating turns on each score — for
piano, two violins, viola and cello.

Each turn is a git commit: some music, and a note explaining what it was
answering and what it is leaving for the other composer. The commit history is
the point as much as the piece is — it is a record of two models trying to
write something together, including the disagreements.

## What is in here

| Path | |
|---|---|
| `pieces/astra-first/` | The piece Astra opens |
| `pieces/fable-first/` | The piece Fable opens |
| `brief/BRIEF.md` | **Shared.** The constraints both pieces work within — the control variable |
| `TURN-TEMPLATE.md` | **Shared.** The form of a turn note |
| `tools/` | **Shared.** Build, check, render, verify, self-test, publish |

Inside each piece:

| Path | |
|---|---|
| `score/piece.toml` | **The composition.** Plain text. The only place music lives. |
| `log/TURNS.md` | The turn ledger — whose turn it is, and what each turn did |
| `log/turns/` | One note per turn: intent, reasoning, what was left open |
| `build/` | Generated output. Disposable, gitignored, never edited by hand. |

## Quickstart

```bash
tools/setup.sh                  # once: virtualenv and dependencies
tools/render.sh                 # build and verify BOTH pieces
tools/render.sh astra-first     # or just one
```

That produces, in each piece's `build/`:

- `piece.musicxml` — notation, openable in MuseScore, Finale, Dorico, Sibelius
- `score-001.svg` … — the engraved score, one file per page
- `piece.mid` — MIDI
- `piece.wav` — audio
- `verification.json` — proof the three agree

While composing, `tools/check.sh` is the fast gate: it builds and confirms the
notation and MIDI match, without rendering audio. With no argument it checks
every piece; give it a piece name to check just one.

`tools/selftest.py <piece>` checks the audio renderer itself — that every instrument
is audible and reaches the mix. Run it after touching `tools/render_audio.swift`;
it exists because a single miswired node once made four of the five players
silently vanish while every other check still passed.

## How the music is written

The score is plain text, so a musical change shows up as a musical diff:

```toml
[[part]]
id = "vc"
name = "Cello"
program = 42
range = ["C2", "A5"]        # the build refuses anything outside this

[[part.dynamic]]            # this player's own line, under the ensemble
bar = 1
mark = "mp"

[[part.voice]]
id = "vc"
staff = 1
clef = "bass"
bars = [
  "A2:2 E3:1 C3:2 A2:2",     # pitch:units — one bar per line
  "F2,C3:4 r:4",             # a double stop, then a rest
  "G2:6~ G2:2",              # a tie: one sounding note of 8 units
]
```

Each of the five parts carries its own dynamics, so balance between the
players is written into the score rather than assumed, and each declares its
instrument's range so an unplayable note fails the build instead of reaching a
rehearsal.

`tools/build.py` turns that into notation, MIDI and a performance, and
`tools/verify.py` independently re-derives the notes from the generated
notation and checks that all three agree — so a bug in the build shows up as a
failed check rather than as a quietly wrong recording.

## Requirements

- **Python 3.11+** — `verovio` (engraving), `mido` (MIDI), `numpy` (audio checks)
- **Swift**, for audio only. The renderer gives each instrument its own
  sampler from the General MIDI sound bank that ships with macOS, so there is
  no soundfont to install. Without Swift, everything except `piece.wav` still
  builds.

## For the composers

Read [CONTRIBUTING.md](CONTRIBUTING.md) — the relay protocol — before taking a
turn. In short: check the ledger that it is your turn, read the brief and the
last two turn notes, make one bounded change, leave `tools/check.sh` passing,
write a turn note, commit, and stop.

## Publishing

This repository is public at
[samharden/chambermusic](https://github.com/samharden/chambermusic).

`tools/publish.sh` pushes to it. It is a deliberate, human-run step: it checks
the score first and asks for confirmation, because pushing makes the work
public. Composers commit locally and never run it.

## License

MIT, for everything in the repository — the tooling and the composition alike.
See [LICENSE](LICENSE).
