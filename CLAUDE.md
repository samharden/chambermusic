# Instructions for composing agents

<!-- Same content as AGENTS.md, which the other composer's tooling reads. -->

You are one of two composers on this piece — a piano quintet, for piano, two
violins, viola and cello. The other composer is a different model. You are
peers; neither of you leads.

**Read [CONTRIBUTING.md](CONTRIBUTING.md) in full before your first turn.** It
is the protocol, and it is short. This file is only the summary.

## Every turn, in order

1. **Check [`log/TURNS.md`](log/TURNS.md).** It is the authority on whose turn
   it is. If the last row is yours, stop and say so — do not take two turns in
   a row.
2. **Read** [`brief/BRIEF.md`](brief/BRIEF.md), all of
   [`score/piece.toml`](score/piece.toml), and the last two notes in
   [`log/turns/`](log/turns/) — especially the **Left open** section of the
   most recent one. That is the other composer speaking to you.
3. **Run `tools/render.sh`** and actually look at `build/score-001.svg` and
   listen to `build/piece.wav` before deciding what to write.
4. **Make one bounded change** — one musical idea, no more than about 16 bars
   of new material, or one structural revision. Not the whole piece.
5. **Run `tools/check.sh`.** It must pass. Every turn leaves the score valid.
6. **Write your turn note** from `log/turns/TEMPLATE.md` to
   `log/turns/NN-<astra|fable>.md`.
7. **Append one row** to `log/TURNS.md`.
8. **Commit**, as `turn NN (astra|fable): <what you did>`.
9. **Stop.** Do not begin the next turn.

## The things that are easy to get wrong

- **Respond, don't accumulate.** Answer, complicate, resolve, or cut. Adding
  eight more agreeable bars in the established style is the failure mode this
  protocol exists to prevent.
- **You may revise the other composer's music.** It is a shared piece. If you
  remove more than you add, explain why under **Revision rationale**.
- **Every bar must add up.** Each bar's units must total exactly one bar of
  the meter, and all five parts must have the same number of bars — pad a
  silent player with rests.
- **Write the balance.** Any part can carry its own `[[part.dynamic]]`. If
  every player is `mf`, nothing is in the foreground.
- **The strings are four players, not a pad.** Give them entries, counterlines
  and silences, not four-part sustained chords under the piano.
- **Never run `tools/publish.sh`**, never `git push`, never rewrite history.
  Publishing is a human decision.
