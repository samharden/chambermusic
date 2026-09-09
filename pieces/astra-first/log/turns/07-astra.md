# Turn 07 — Astra

**Piece:** astra-first
**Bars touched:** 61–96 (new); shorter expression marks at 51, 53, 55, 57 and 59; title and completion metadata
**Builds clean:** yes — both pieces pass the notation/MIDI and full audio checks; five notation regression tests pass.

## What I did

I completed the return and coda, and named the quintet **A Semitone from
Home**. Your running piano continues at 61, but its E becomes F, making the
dominant seventh audible. The texture thins, visits Db/F and F minor, and
returns through diminished harmony and the cadential six-four to G7. The
viola brings back its exact opening two bars at 73, with B's running piano
quietly underneath in C minor. Violin I takes the gesture at 77. At 78,
F major gives the piano's A-natural a consonant home; F minor at 79 then
turns it into Ab. The cello's augmented opening returns at 81, and this time
gets to complete its answer. An arrival at 85 and cadence at 87–88 leave a
shared breath. The coda at 89 slows to quarter = 80: the piano itself sings
C–G–Ab–G, answered by the lower strings. The final dominant resolves B to C
and F to Eb at 95; the quiet echo at 96 contains only C, Eb and G, with all
five players releasing together.

## Why

Your pivot at 55–58 earns the return to C. I wanted to answer the live
motion you handed over at 60, and to let the viola reclaim the opening at
73 as you suggested. Twelve more bars of an unchanged G figure would have
spent that momentum without developing it, so the retransition moves
through a predominant region and progressively withdraws. A-prime keeps
the opening's semitone and minor third, but carries B's running texture
inside it. The A-natural is admitted over F major before becoming Ab over
F minor; it has a harmonic purpose rather than remaining an unresolved
collision. Finally, the piano adopts the viola's semitone itself. That is
the resolution of their disagreement, and the reason for the title.

The piano **leads** the retransition at 61–64, **supports and answers** the
lower voices at 65–72, **supports** the viola and violin return at 73–80,
and leaves the cello in the foreground at 81–84. It joins the arrival at
85–88, **leads** the coda's opening at 89–90, then yields to the lower
strings and supplies the final cadence. Independent dynamics keep the
melodic player ahead of the piano. New string writing is monophonic, with
rests and separate entries; no new sustained note exceeds one bar. The
largest new piano chord in either hand is a major sixth.

The human explicitly asked Astra to close the piece after turn 6. This
36-bar final turn follows that direction instead of the usual approximate
16-bar ceiling and the ordinary two-composer completion sequence. The
brief's A 1–32, B 33–72, A-prime 73–end structure remains intact, and the
96-bar piece lasts 4:04 before its four-second audio release. All pitches
and rhythms in the first 60 bars are preserved. The shorter expression
marks make that existing music fit the printed page more clearly.

I reviewed the synthesized rendering and engraved pages, checked the tonal
arrivals, instrumental ranges and piano spans, and exported and visually
checked the ten-page PDF. The audio peaks at -8.24 dBFS without clipping.
A separate tooling commit, `f53fd14`, adds a final barline only to scores
marked complete, with a regression test. The local build contains the PDF,
MusicXML, MIDI and WAV. No publication was performed.

## Left open

No further relay turn is scheduled: the human asked for this to be the
ending. Your diminished-seventh pivot remains the route home, and your
running figure survives underneath the return. The final tonic is C minor;
the piano's whole-tone challenge is answered through modal mixture and its
eventual adoption of Ab, rather than through an unresolved final chord.

## Status

I think the piece is finished.

Completion is at the human's explicit direction. Fable's turn 6 status
remains `continuing`; this note does not claim a second composer's approval.
