# Turn 02 — Fable

**Piece:** astra-first
**Bars touched:** 13–21 (new); bar 12 untouched in the end
**Builds clean:** yes — `tools/check.sh` passes for both pieces; `tools/render.sh astra-first` renders, peak -13.98 dBFS.

## What I did

I admitted the Ab. Violin I re-sounds its Ab4 on the downbeat of bar 13 and
the piano, for the first time, agrees with it: F2/C3 in the bass, Ab4/C5 in
the right hand, pp. Under F the disputed note is just the third of F minor.
On that floor the cello takes the lead it claimed in bar 9 and sings the
first sustained line in the piece — the opening gesture augmented to double
length (6–2–4–4 in eighths): F–C, Db–C (the semitone, transposed), then the
descent Bb–Ab–G–F. In bar 16 the viola echoes Db–C an octave below, in its
low register, and the piano falls silent. Bars 17–18 the cello is alone,
exactly as the viola was in bar 1, and plays the opening at its original
pitch — C4–G4–Ab4–G4 — twice as slowly. Bar 19 is the one full bar: the
cello's descent F–Eb–D–C, Violin II a counterline Ab–G–F above it, the viola
its own bar 6 (C–Bb–Ab) below, Violin I entering late with F5–Eb5, the piano
a G/D under the second half. Bar 20 the ensemble drops out and the piano
plays its bar 4 challenge verbatim, C5–G5–A5–G5, while the cello holds Ab3
over a G2 pedal: A-natural and Ab in the same bar for the first time. Bar 21
the piano answers itself with the major-mode descent F–E–D–C over C3 and the
cello's G3; both lower voices release on beat 4 and the piano's C5 stands
alone, mirroring your Ab alone in bar 12.

Piano role by bar: **supporting** in 13–16 (pedal points, no voice-leading of
its own), **absent** in 17–18, **supporting** in 19, **opposing** in 20–21.
All string writing is single-line; the cello's C4–Ab4 in 17–18 is high tenor
but ordinary. Largest piano span within a hand is a fifth.

## Why

Twelve bars of one- and two-bar fragments is a strong opening but it is not
yet a piece anyone can sing; someone had to hold the floor. You handed it to
the cello in bar 9 and offered the Ab as something that could "become a
consonance under a different bass" — I took that option literally, because
resolving Ab to G would have closed the argument and forcing a change of
direction would have discarded it. F minor keeps the Ab and keeps C in view.
Your piano conceded the semitone in bar 11; I let it stay conciliatory for
seven bars and then withdrew the concession in bar 20, because a piano that
has stopped arguing is just an accompanist, and the brief says it is not.

I did not tie Ab across the barline as you invited. Cross-bar ties are a
tooling bug: `flatten()` merges them for MIDI but the MusicXML emitter resets
its pending set every bar, so the notation shows an unclosed tie and
`verify.py` fails. Rearticulating was musically fine here. Either of us can
fix `tools/build.py` in a tooling commit; I did not want to mix it into this
turn.

## Left open

Bar 21 is C over G in three octaves with no third. Both thirds have now been
heard in passing — the strings' Eb throughout, the piano's E5 on the second
beat of bar 21 — and neither has been allowed to sit. I would like to hear
whose third it is, or whether you refuse to say.

The A-natural/Ab clash in bar 20 is the first time both are sounded in one
bar. I put them a tenth apart and mp; you could bring them closer, or make
one of them give way.

Bars 22–32 remain for the end of A. The cello has had its line and stopped;
Violin I has done almost nothing since bar 12 but hold Ab and offer two
notes in bar 19 — it has the most unspent capital. The upper strings have
never played a sustained line together. The lower register below C3 has
barely been used except as pedal.

B begins at 33 in a new key area. F minor is now in the room as a candidate,
but I would not object to it being a feint.

## Status

continuing
