# notes.md: lab notebook

Append-only. One short entry per experiment: hypothesis, outcome, next idea. Newest at the bottom.
Stock profile: `MID2_Priest_Shadow` (Voidweaver, level 90, void elf). Archon variant in `reference/` for hero-tree swaps.
Keep criterion and playability rules: `program.md`.

## exp 1 — Archon instead of Voidweaver (talents only)
Hypothesis: the stock MID2 profile ships Voidweaver, but the Archon reference profile uses the identical APL, so the hero tree is a free one-line swap worth testing first.
Outcome: **kept**. raid 218.6k → 231.3k (+5.8%, z≈+56), dungeon 257.4k → 268.3k (+4.2%, z≈+37), both confirmed at target_error 0.1.
Caution: a gap this large on the stock profile suggests either the Voidweaver APL is under-tuned in simc 1210-01, or Voidweaver is chosen for reasons sims don't see (movement, burst windows). Worth a Voidweaver-specific APL pass later rather than writing Voidweaver off.
Next: with Archon as the new base, try talent swaps below the hero tree (dungeon first), then opener/execute priority reorders.

## exp 2 — Idol of Yogg-Saron → Idol of C'Thun (row 10, same cost)
Hypothesis: the Archon build takes N'Zoth + Yogg-Saron; C'Thun procs off Mind Flay / Mind Flay: Insanity channels, which Archon leans on, and its Void Lasher should add AoE for `dungeon`.
Outcome: **not kept**, regressed on both. raid 231.3k → 229.7k (−0.7%, z≈−6.5), dungeon 268.3k → 264.3k (−1.5%, z≈−13.3). Yogg-Saron's VT-driven Thing from Beyond scales with the many VTs in DungeonSlice, so the swap hurt dungeon more than raid. Reverted.
Method: simc's JSON never names talents, so decode a hash with a scratch profile carrying `html=` and read the talent table (`runs/decode/`). Same-row swaps go in `talents.simc` as `spec_talents+=idol_of_yoggsaron:0/idol_of_cthun:1` under the hash; simc regenerates the hash but does not check tree connectivity, so a swap outside a choice node still needs a human eyeball before anyone plays it.
Archon loadout for reference (untaken spec talents): Misery, Intangibility, Thought Harvester, Shadowy Insight, Voidtouched, Dark Thoughts, Improved Voidform, Subservient Shadows, Distorted Reality, Spectral Horrors, Instilled Doubt, Deathspeaker, Death and Madness, Mind Devourer, Madness Weaving, Idol of Y'Shaarj, Idol of C'Thun, Shadowfiend/Mindbender/Inescapable Torment. Hero row 2–4 untaken: Shock Pulse, Heightened Alteration, Realized Potential, Energy Compression.
Next: row-8 swap Auspicious Spirits → Mind Devourer or Deathspeaker (the APL already handles both), then an opener reorder.

## exp 3 — Auspicious Spirits → Mind Devourer (row 8, same cost)
Hypothesis: Mind Devourer's free, instant Shadow Word: Madness procs off Mind Blast, which the Archon build casts a lot; the APL already has `buff.mind_devourer.react` branches, so this is a pure talent test with no APL change.
Outcome: **not kept**, regressed on both. raid 231.3k → 228.8k (−1.1%, z≈−10.0), dungeon 268.3k → 263.4k (−1.8%, z≈−16.5). In the exp 2 decode run Auspicious Spirits was ~8% of all Insanity gained (194/2470); losing that slows the Mind Flay: Insanity / Void Volley loop Archon lives on, and Mind Devourer's saved GCDs don't make it back. Dungeon hurt more because more apparitions fly in multi-target. Reverted.
Legality note: Tormented Spirits (row 9) and Idol of Yogg-Saron (row 10) sit under Auspicious Spirits in the tree; simc accepted the override but an in-game loadout dropping AS may need a different path. Moot since it lost anyway.
Next: row 8 is settled (AS stays). Try row-10 Idol of N'Zoth → Idol of Y'Shaarj (same cost), then the opener: move `void_volley,if=cooldown.voidform.up` above `shadow_word_madness` so Voidform opens with more Insanity banked.
