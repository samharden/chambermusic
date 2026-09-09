# Instructions for composing agents

<!-- Same content as AGENTS.md, which the other composer's tooling reads. -->

You are one of two composers writing **two** piano quintets — for piano, two
violins, viola and cello. The other composer is a different model. You are
peers; neither of you leads.

The two pieces are the same brief with one difference: who moves first.

| Piece | Turn 1 |
|---|---|
| `pieces/astra-first/` | Astra |
| `pieces/fable-first/` | Fable |

**Keep them independent.** Do not carry material between them, and do not try
to make them complement each other. Each turn answers only its own piece.

**Read [CONTRIBUTING.md](CONTRIBUTING.md) in full before your first turn.** It
is the protocol, and it is short. This file is only the summary.

## Every turn, in order

1. **Pick a piece, and check its `log/TURNS.md`.** It is the authority on
   whose turn it is *in that piece*. If the last row is yours, stop and say
   so — it may still be your turn in the other piece.
2. **Read** [`brief/BRIEF.md`](brief/BRIEF.md), all of that piece's
   `score/piece.toml`, and the last two notes in its `log/turns/` —
   especially the **Left open** section of the most recent one. That is the
   other composer speaking to you.
3. **Run `tools/render.sh <piece>`** and actually look at that piece's
   `build/score-001.svg` and listen to its `build/piece.wav` before deciding
   what to write.
4. **Make one bounded change** — one musical idea, no more than about 16 bars
   of new material, or one structural revision. Not the whole piece.
5. **Run `tools/check.sh`.** It must pass, for both pieces. Every turn leaves
   every score valid.
6. **Write your turn note** from [`TURN-TEMPLATE.md`](TURN-TEMPLATE.md) to
   `pieces/<piece>/log/turns/NN-<astra|fable>.md`.
7. **Append one row** to that piece's `log/TURNS.md`.
8. **Commit**, as `<piece> turn NN (astra|fable): <what you did>`.
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
