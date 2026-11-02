# program.md: the researcher's brief

You are running theorycrafting experiments for a **Shadow Priest** in World of Warcraft: Midnight,
using SimulationCraft. You work alone, in a loop. Each turn you may run experiments, then you must
log what happened and stop. The next turn starts by reading this file, `results.tsv` and `notes.md`.

## Tracks

Players run different loadouts for raid and Mythic+, so this search does too. Each track has its own
talents and APL and is scored on its own profile. Pick **one track per turn**; alternate unless the
notes say one track is stuck.

| track | files | simc fight_style | stands for |
|---|---|---|---|
| `raid` | `candidate/raid/{talents,apl}.simc` | `Patchwerk`, 300s, 1 target | single-target raid boss |
| `dungeon` | `candidate/dungeon/{talents,apl}.simc` | `DungeonSlice` | Mythic+ pull pattern |

`candidate/baseline.simc` (character, gear, consumables) is shared and fixed.

## Goal

Raise DPS on a track's profile **without** violating the playability rules. Keep what works. Record
everything, including failures, because the failures are half the value.

A change is **kept** on its track only if `dps_new - dps_old > 2 * sqrt(err_new^2 + err_old^2)`
against the track's last kept result. After a keep, also sim the change on the *other* profile and
record the number in notes (one line) so cross-track effects are visible; it does not affect the keep.

## Playability rules (hard)

1. No APL condition may reference a quantity a player cannot see or estimate in real time
   (e.g. exact `time_to_die`, `dot.remains<0.73`). Round to things a human tracks: half seconds,
   stack counts, "under 20% health".
2. At most one new conditional branch per kept change. Complexity is a cost: `apl_lines` is logged
   on every result and must not grow more than +3 across any five consecutive keeps.
3. No cancel-aura or clip tricks that depend on sub-GCD timing.
4. Talents must be a legal in-game loadout: respect tree paths and point budgets, not just what simc
   accepts. If an override skips a prerequisite node, say so in notes and treat the result as
   provisional.
5. Do not change gear, consumables, buffs, or the fight length.

## Procedure, every turn

1. Read `results.tsv` tail and `notes.md` tail. Pick the track. Decide one hypothesis. Write it down first.
2. Make the edit in that track's directory only. One idea per experiment.
3. `uv run tools/sim.py --track raid|dungeon` (default `target_error` 0.2). Use `--target-error 0.1` only to confirm a keep.
4. Compare with the track's last kept row (`tools/log.py` computes delta and z for you).
5. Log with `tools/log.py <exp> <track> <dps> <err> <apl_lines> <hash> yes|no "<hypothesis>"`; add 1-3 lines to `notes.md`.
6. If kept: leave the candidate. If not: `git checkout -- candidate/`.
7. `git add -A && git commit -m "exp <n> [<track>]: <hypothesis>"`. Stop.

## Where the value probably is

- **dungeon** track: the stock build is raid-shaped. AoE and cleave talents, DoT-spread priority,
  cooldown usage per pull rather than per fight. This is the least-explored space.
- **raid** track: the stock Archon APL is expert-tuned; expect small or no wins from reorders.
  Look at execute, at cooldown alignment with trinkets, and at hero-tree choice nodes.
- A rejected idea with a clear mechanism explanation is worth as much as a keep. Say why it lost.

## Tools

- `uv run tools/sim.py --track raid|dungeon [--fight other] [--target-error 0.1] [--detail|--json]`
  Run JSON in `runs/` has per-ability stats, buff uptimes, gains and procs. `--detail` prints the top
  damage sources with cast counts and the top buff uptimes; `--json` includes them as `top_damage`
  and `uptimes`. Use these to explain *why* a change won or lost, not just that it did.
- `uv run tools/talents.py --track raid|dungeon` (or a talent string) decodes the loadout into
  class / spec / hero rows with ranks. Use it before any talent swap instead of guessing from hashes.
- `uv run tools/log.py ...` appends a result row; `uv run tools/report.py` renders the summary.

## What not to do

- Don't edit `baseline.simc` or `tools/`. If a tool is broken, write it in `notes.md` and stop.
- Don't run more than ~10 sims per turn. Don't lower `target_error` below 0.1.
- Don't write outside this repo. The repo is the record.
- Don't re-run an experiment already in `results.tsv` unless the notes give a reason.
