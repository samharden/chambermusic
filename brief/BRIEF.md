# The brief

The constraints both composers work within. Binding on both. To change
anything here, propose it in a turn note under **Brief proposal**; see
*Changing the brief* in [CONTRIBUTING.md](../CONTRIBUTING.md).

> **This brief is a starting point, filled in with defaults so the repository
> is runnable from the first commit. Replace it with what you actually want
> the piece to be before turn 1.**

## The piece

- **Instrument:** solo piano (one part, two staves)
- **Length:** 48–80 bars, roughly 2–4 minutes
- **Meter:** 4/4
- **Key centre:** C, free to move
- **Tempo:** around ♩=96, free to change at section boundaries

## Form

A clear sectional shape both composers can navigate and refer to by name:

| Section | Bars | |
|---|---|---|
| A | 1–16 | State the material |
| B | 17–32 | Depart from it |
| A′ | 33–48 | Return, changed by the departure |

Extend or reshape this by proposal, not unilaterally.

## Constraints

- **Playable by one pianist.** Hands must not need the same key at the same
  moment, and no chord should exceed a comfortable stretch — a ninth at the
  outside. `tools/verify.py` does not currently check this; you must.
- **The piece has to hold together.** Whatever either composer introduces
  should be answerable. Do not write a gesture the other composer has no way
  to respond to.
- **Notate what you mean.** Accidentals are explicit in the source; if a
  passage depends on pedalling or on a tempo inflection, write it in the
  tempo map, the `[marks]`, or the turn note.

## What this piece is trying to be

<!-- Replace this section. It is the only part of the brief that is about
     music rather than logistics, and it is the part that actually shapes what
     gets written. Say what the piece should feel like, what it should avoid,
     what would count as it going wrong. -->

Something that sounds composed rather than generated: material that is
introduced, developed, and answered, where a listener can hear the second half
responding to the first.

**Avoid:** ambient wash with no structural argument; four-bar loops repeated
without development; a texture that never changes.
