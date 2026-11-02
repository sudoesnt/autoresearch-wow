# notes.md: lab notebook

Append-only. One short entry per experiment: hypothesis, outcome, next idea. Newest at the bottom.
Stock profile: `MID2_Priest_Shadow` (Voidweaver, level 90, void elf). Archon variant in `reference/` for hero-tree swaps.
Keep criterion and playability rules: `program.md`.

## exp 1 — Archon instead of Voidweaver (talents only)
Hypothesis: the stock MID2 profile ships Voidweaver, but the Archon reference profile uses the identical APL, so the hero tree is a free one-line swap worth testing first.
Outcome: **kept**. raid 218.6k → 231.3k (+5.8%, z≈+56), dungeon 257.4k → 268.3k (+4.2%, z≈+37), both confirmed at target_error 0.1.
Caution: a gap this large on the stock profile suggests either the Voidweaver APL is under-tuned in simc 1210-01, or Voidweaver is chosen for reasons sims don't see (movement, burst windows). Worth a Voidweaver-specific APL pass later rather than writing Voidweaver off.
Next: with Archon as the new base, try talent swaps below the hero tree (dungeon first), then opener/execute priority reorders.
