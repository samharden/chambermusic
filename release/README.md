# Release

Finished artifacts are committed here deliberately, when the piece is done:
the engraved score, the MIDI, and the audio, alongside a copy of the
`build/verification.json` that vouches for them.

Everything in `build/` is disposable and gitignored. Nothing lands here
automatically.

## The finished pieces

Both relays closed at turn 7.

| Piece | Title | Opens | Bars | Listen | Score |
|---|---|---|---|---|---|
| `astra-first/` | *A Semitone from Home* | Astra | 96 | [piece.m4a](astra-first/piece.m4a) · [piece.mid](astra-first/piece.mid) | [PDF](astra-first/a-semitone-from-home-score.pdf) · [SVG pages](astra-first/) |
| `fable-first/` | *The Disputed Third* | Fable | 88 | [piece.m4a](fable-first/piece.m4a) · [piece.mid](fable-first/piece.mid) | [SVG pages](fable-first/) |

Each directory holds:

- `score-NNN.svg` — the engraved pages, one file per page, exactly as
  `tools/build.py` produced them from `score/piece.toml`
- `piece.mid` — the MIDI, from the same build
- `piece.m4a` — the audio rendered by `tools/render_audio.swift` from that
  MIDI, transcoded from the build's WAV to 256 kbps AAC so the repository
  stays small
- `verification.json` — `tools/verify.py`'s independent check that the
  notation, the MIDI and the performance all agree

The `.pdf` in `astra-first/` was exported by hand from the SVG pages.
