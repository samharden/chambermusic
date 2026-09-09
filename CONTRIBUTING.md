# The Relay Protocol

Two composers work on one piece, a piano quintet: **GPT-6 Astra** and
**Fable 5.1**. They are peers. Neither is the lead, neither is the assistant, and neither gets the
last word by default.

They work in a **relay**: one composer takes a turn, commits it, and hands
off. The other reads what happened and answers it. The git history is meant
to read as a musical conversation — which means each turn has to be legible
as a *response* to the one before it, not just more notes appended to a file.

---

## The one-paragraph version

Check `log/TURNS.md` to confirm it is your turn. Read `brief/BRIEF.md`, the
current `score/piece.toml`, and the last two turn notes. Make a bounded change
to the score. Run `tools/check.sh`. Write a turn note saying what you did,
why, and what you are leaving open. Add a row to `log/TURNS.md`. Commit.
Stop.

---

## What a turn is

A turn is **one commit** that changes exactly three things:

| File | Change |
|---|---|
| `score/piece.toml` | The music itself |
| `log/turns/NN-<composer>.md` | A new turn note (see template) |
| `log/TURNS.md` | One appended row in the ledger |

If a turn touches anything else — tooling, the brief, the README — that is a
separate commit, made outside the relay, and it does not consume a turn.

### A turn is bounded

Write **one musical idea per turn**. A section, a countermelody, a harmonic
reinterpretation of eight bars, a transition, a decision to cut something.

Do not compose the whole piece in one turn. The point of the relay is that
the other composer gets to shape the material while it is still soft. A turn
that fills in every remaining bar is technically legal and defeats the entire
exercise. If you find yourself with more ideas than fit in one turn, put the
extras in the **Left open** section of your note and let the other composer
decide whether to take them.

A useful ceiling: **no more than ~16 bars of new material per turn**, or one
structural revision of existing material. Go under it freely.

---

## Reading before writing

Before you touch the score, read in this order:

1. **`brief/BRIEF.md`** — the constraints. These bind both composers. If you
   want to change them, see *Changing the brief* below; you may not simply
   ignore them.
2. **`score/piece.toml`** — the whole thing, not just the end. You are
   responding to a piece, not a stub.
3. **The last two turn notes** in `log/turns/`. Especially the **Left open**
   section of the most recent one — that is the previous composer speaking
   directly to you.
4. **Render it** with `tools/render.sh`, then look at `build/score-001.svg`
   and *listen to* `build/piece.wav`. Both reveal things a text diff hides:
   voice crossings, register collisions, two hands wanting the same key, a
   line that reads cleanly in the source and is unplayable on a staff.

---

## Responding, not just continuing

The most common failure mode in a two-composer relay is **polite
accumulation**: each turn adds eight more bars in the established style, and
nothing is ever questioned, so the piece has no argument in it.

A turn is stronger when it does one of these:

- **Answers** the previous idea — inverts it, augments it, reharmonizes it,
  gives it to the other voice.
- **Complicates** it — introduces the tension that the material has been
  avoiding.
- **Resolves** something the other composer left deliberately unresolved.
- **Cuts** — removes material that is not earning its place, and says so.

You have full standing to revise the other composer's material. It is a
shared piece, not two adjacent solos.

### The revision rule

You may change anything. But if a turn **deletes or rewrites more of the
other composer's material than it adds**, the turn note must have a
**Revision rationale** section explaining the musical reason.

This is not a permission gate — you do not need agreement to make the change.
It is a *record* requirement. A large revision with a stated reason is a
contribution. A large revision with no stated reason is indistinguishable
from not having read the other composer's work.

---

## Disagreement

If you think the previous turn was a mistake, say so in your turn note, in
plain terms, and then **either** revise it **or** build on it — not both, and
not neither.

- Revising it is a real answer.
- Building on it while noting the reservation is a real answer.
- Reverting it silently is not.
- Writing "interesting choice!" and working around it is not.

If the two composers revise each other's same eight bars back and forth
**three times**, stop. Both composers write a short position in their turn
notes, and a human decides. Note it in `log/TURNS.md` with status `STALLED`.
Do not keep trading reverts.

---

## Leaving the score valid

**Every turn must leave `tools/check.sh` passing.** No exceptions, including
mid-piece and including turns that are mostly deletion.

```bash
tools/check.sh
```

It builds the score and then verifies, by re-deriving the notes independently
from the generated notation, that the engraved score and the MIDI contain
exactly the same music. It is fast; run it as often as you like.

Before handing off, also run the full render at least once:

```bash
tools/render.sh
```

That adds the audio and checks it against the MIDI. **Listen to it.** A piece
that looks right in the source and sounds wrong is wrong, and you are the only
one who can hear it before the other composer does.

### Writing notes

Each entry in a voice's `bars` array is one bar:

```toml
bars = [
  "A4:2 D5:1 C5:2 A4:2",     # pitch:units
  "F4,A4,C5:4 r:4",          # a chord, then a rest
  "G4:6~ G4:2",              # tied across a beat: one sounding note of 8
]
```

- One **unit** is `settings.unit` (an eighth by default).
- A chord token in a **string** part is a double or triple stop. Write one only
  if it is reachable; otherwise give the note to another player.
- Every bar must add up to exactly one bar of `settings.meter`. This is the
  single most common mistake, and `tools/check.sh` reports it with the bar
  number and what it found.
- Accidentals are written into the pitch (`Bb3`, `F#5`), never assumed from
  the key signature. Spelling on the printed page follows `settings.key`.
- All voices must have the **same number of bars**. When you extend the piece,
  extend every one of the five parts, padding with rests (`r:8`) where a
  player is silent.
- Each part declares its instrument's `range`, and the build **refuses** notes
  outside it. This catches the unplayable, not the ill-advised — see the brief
  for where each instrument actually sounds good.
- Any part may carry its own `[[part.dynamic]]` line. Use it: balance between
  five players is most of the craft, and if everything is `mf`, nothing is
  foreground.

### What the format does not do

Know these before you plan around them:

- **No tuplets.** For triplets, set `settings.unit` finer (a sixteenth or a
  thirty-second) and spell the rhythm out in units.
- **Tempo and dynamics change only at bar lines.** A `cresc.` inside a bar has
  to be written as a dynamic on the next bar, or described in `[marks]`.
  Tempo is always ensemble-wide; dynamics can be per player.
- **No slurs, articulation, bowing, or fingering.** No pizzicato, mutes, or
  harmonics either. Phrasing and playing instructions are carried by the
  `[marks]` text and by the turn notes.
- **Ties join two adjacent notes of the same pitch**, and cannot cross a rest.

If a musical idea genuinely needs something the format lacks, say so in your
turn note. Extending `tools/build.py` is a tooling commit, made outside the
relay, and either composer may do it — but do not silently work around a
limitation in a way that makes the source lie about the music.

## Turn notes

Copy `log/turns/TEMPLATE.md` to `log/turns/NN-<composer>.md`, where `NN` is
the zero-padded turn number and `<composer>` is `astra` or `fable`.

The note is not ceremony. It is the only channel the two composers have for
talking to each other about intent, and **Left open** is the most important
section in the repository: it is where a turn tells the next one what it is
being handed.

Write it for the other composer, not for a reader looking back. Be specific.
"Left the cadence unresolved" is weak. "Bar 24 lands on a V7 and stops — I
want to hear what you do instead of the tonic" is a real handoff.

---

## The ledger

`log/TURNS.md` holds one row per turn and is the authority on **whose turn it
is**. If the last row is yours, it is not your turn; stop and say so.

---

## Commits

One commit per turn, message formatted:

```
turn 07 (fable): reharmonize the B section over a pedal D
```

- lowercase, imperative or descriptive, one line
- always name the turn number and the composer
- the body is optional; the turn note carries the reasoning

---

## Changing the brief

`brief/BRIEF.md` binds both composers. Either composer may **propose** a
change to it — a new section, a different ending, dropping a constraint that
turned out to be wrong — but a proposal is written in a turn note under
**Brief proposal**, not applied unilaterally.

The other composer responds in their next turn note, accepting or declining.
If accepted, the *accepting* composer edits `brief/BRIEF.md` in a separate
commit outside the relay, quoting both turn notes in the commit message.

The reason for the friction: the brief is the only thing keeping two
independent composers writing the same piece.

---

## What composers never do

- **Never run `tools/publish.sh`.** Publishing is a human decision, made
  once, deliberately. It makes the work public and is not easily undone.
- **Never `git push`**, never create remotes, never open pull requests.
- **Never rewrite history** — no amending another composer's commits, no
  force-pushing, no rebasing the relay. The log is the record.
- **Never take two turns in a row**, even if the other composer is slow, and
  even if you have a good idea. Put the idea in **Left open**.
- **Never edit another composer's turn notes.** Respond in your own.

---

## Finishing

The piece is done when the brief's structure is complete and both composers
have, in consecutive turn notes, said so under **Status**. Then a human
reviews, and runs `tools/publish.sh` if they want it public.

Either composer may propose finishing early, the same way as a brief change.
