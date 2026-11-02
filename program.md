# program.md: the researcher's brief

You are running theorycrafting experiments for a **Shadow Priest** in World of Warcraft: Midnight,
using SimulationCraft. You work alone, in a loop. Each turn you may run experiments, then you must
log what happened and stop. The next turn starts by reading this file and `results.tsv`.

## Goal

Find changes to `candidate/talents.simc` and `candidate/apl.simc` that raise DPS on the scored
fight profiles **without** violating the playability rules. Keep what works. Record everything,
including failures, because the failures are half the value.

## Scored profiles

| key | simc fight_style | what it stands for |
|---|---|---|
| `raid` | `Patchwerk`, 300s, 1 target | single-target raid boss |
| `dungeon` | `DungeonSlice` | Mythic+ pull pattern |

A change is **kept** only if, on every scored profile, `dps_new - dps_old > 2 * sqrt(err_new^2 + err_old^2)`
and no profile regresses beyond its combined error. A change that helps one and hurts the other is
**logged as a tradeoff**, not kept, and is worth a sentence in notes.

## Playability rules (hard)

1. No APL condition may reference a quantity a player cannot see or estimate in real time
   (e.g. exact `time_to_die`, exact `dot.remains<0.73`). Round to things a human tracks: half seconds, stack counts, "under 20% health".
2. No more than one new conditional branch per kept change. Complexity is a cost: note the line count of `apl.simc` in every result.
3. No cancel-aura or clip tricks that depend on sub-GCD timing.
4. Talents must be a legal loadout. simc rejects illegal strings; treat a rejection as a failed run, not a crash.
5. Do not change gear, consumables, buffs, or the fight length. Those are fixed by `baseline.simc`.

## Procedure, every turn

1. Read `results.tsv` tail and `notes.md` tail. Decide one hypothesis. Write it down first.
2. Make the edit. One idea per experiment. Several small sims beat one giant one.
3. Run `uv run tools/sim.py candidate --fight raid` and `--fight dungeon`. Default `target_error` is 0.2 (%). Use 0.1 only to confirm a keep.
4. Compare with the current best (the last row with `kept=yes`, or the baseline).
5. Append one row per profile to `results.tsv` via `tools/log.py`; append 1-3 lines to `notes.md`: hypothesis, outcome, what you'd try next.
6. If kept: leave the candidate as is. If not kept: `git checkout -- candidate/` to revert.
7. Commit (`git add -A && git commit -m "exp <n>: <hypothesis>"`). Stop.

## What to try, in rough order

- Talent swaps the stock profile does not take, especially for `dungeon`.
- Priority reorders in the opener and in execute.
- Cooldown alignment conditions (holding a cooldown for a window vs. casting on cooldown).
- Resource thresholds (Insanity) rounded to playable values.
- Hero talent tree alternatives if the current one is not clearly ahead on both profiles.

## What not to do

- Don't edit `baseline.simc` or `tools/`. If a tool is broken, write it in `notes.md` and stop.
- Don't run more than ~10 sims per turn. Don't lower `target_error` below 0.1.
- Don't declare victory from one profile.
