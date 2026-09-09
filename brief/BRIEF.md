# The brief

The constraints both composers work within. Binding on both. To change
anything here, propose it in a turn note under **Brief proposal**; see
*Changing the brief* in [CONTRIBUTING.md](../CONTRIBUTING.md).

## The piece

A **piano quintet** — piano, two violins, viola, cello. The standard Schumann
/ Brahms / Dvořák ensemble, and the standard problem that comes with it: one
instrument can outweigh the other four.

- **Length:** 80–160 bars, roughly 4–7 minutes
- **Meter:** 4/4 to begin; may change by proposal
- **Key centre:** C, free to move
- **Tempo:** around ♩=96, free to change at section boundaries

## Form

A clear sectional shape both composers can navigate and name:

| Section | Bars | |
|---|---|---|
| A | 1–32 | State the material; establish who owns it |
| B | 33–72 | Depart — new key area, redistributed texture |
| A′ | 73–end | Return, changed by the departure |

Extend or reshape this by proposal, not unilaterally.

## Writing for the ensemble

This is the part that makes chamber music different from writing a piano piece
with strings added on top.

**The strings are four independent players, not a pad.** If all four move in
the same rhythm for long stretches, you have written a chorale with a piano
accompaniment. Give them entries, counterlines, and silences. A player who
rests for eight bars and then enters is making a stronger statement than one
who never stops.

**The piano is not the accompanist, and it is not the soloist.** It is the
loudest instrument in the room and the only one that can play its own harmony.
Decide, in each section, what it is doing: doubling, opposing, supporting, or
leading. Say which in your turn note.

**Balance is written, not assumed.** A cello line under four other players
needs its own dynamic. Any part can carry `[[part.dynamic]]` independently —
use it. If everything is `mf`, nothing is foreground.

**Leave room.** Five instruments playing continuously is a wall. The texture
should thin and thicken; that contour is a large part of the piece's argument.

## Ranges

The build **refuses** any note outside an instrument's physical range. Those
limits are in `score/piece.toml` and are a floor, not a target:

| | Physical range | Where it actually sounds good |
|---|---|---|
| Violin | G3–E7 | G3–E6; above that it thins and tenses |
| Viola | C3–E6 | C3–C5; the low register is its voice, use it |
| Cello | C2–A5 | C2–E4; the tenor register (C3–E4) sings |
| Piano | A0–C8 | Avoid the extremes except deliberately |

## Playability

The tools do not check these. You must.

- **Strings are monophonic** unless you mean a double stop. A chord token in a
  string part is a double/triple stop: only write one if the notes are
  reachable, and prefer intervals with an open string. When in doubt, give the
  note to another player — you have four of them.
- **No bow can sustain forever.** A tied note running many bars needs to be
  playable in one breath or it needs a rearticulation.
- **The pianist has two hands.** They must not need the same key at the same
  moment, and no single chord should exceed a comfortable stretch — a ninth at
  the outside.

## What this piece is trying to be

<!-- Replace this section if you want something else. It is the only part of
     the brief that is about music rather than logistics, and it is the part
     that actually shapes what gets written. -->

Something that sounds composed rather than generated: material that is
introduced, developed, and answered, where a listener can hear the second half
responding to the first — and where the five players sound like five people
who are listening to each other.

**Avoid:** ambient wash with no structural argument; four-bar loops repeated
without development; strings used only as sustained padding under the piano;
a texture that never changes.
