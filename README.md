# autoresearch-wow

**Autoresearch for World of Warcraft theorycrafting.** An agent edits a character's talents and
rotation (the SimulationCraft APL), sims it, keeps what improved, logs everything, repeats. You
sleep. In the morning you read `results.tsv` and the agent's notes.

> Pre-alpha. Shadow Priest first. Nothing here is a recommendation yet. MIT licensed.

## The loop

```
          ┌────────────────────────────────────────────────┐
          │  program.md  (goal, rules, what "better" means) │
          └────────────────────────────────────────────────┘
                               │ read by
                               ▼
   results.tsv ◀── log ──  Claude Code  ── edits ──▶ candidate/*.simc
        ▲                      │
        │                      │ runs
        │                      ▼
        └──── parse ────  tools/sim.py  ── simc ──▶ runs/<id>.json
```

Three files matter: `program.md` is the agent's brief, `candidate/` is the thing being evolved,
`results.tsv` is the lab notebook. `tools/sim.py` is plumbing. That's the whole method, on purpose:
if it needs more than this to be legible it isn't the autoresearch pattern anymore.

## What "better" means here

SimulationCraft is Monte Carlo. Every DPS number comes with an error. A change is kept only when
the improvement clears the combined error with margin on **every** fight profile it is scored on,
and when it doesn't break the playability rules in `program.md`. Raid and dungeon profiles are
scored separately; a build that trades one for the other is reported, not kept.

## Why it isn't Raidbots

Raidbots sims the candidates you give it. This searches: the agent reads what happened, forms a
hypothesis, and tries the next thing. It also edits the rotation, which no public tool does,
because rotation edits are where "simmed higher" and "a human can play this" come apart. That gap
is the interesting part and the reason a playability cost is in the brief.

## Run it

```
# one-time
cmake -S vendor/simc -B vendor/simc/build -DBUILD_GUI=OFF && cmake --build vendor/simc/build -j --target simc
uv sync

# baseline
uv run tools/sim.py candidate/baseline.simc --fight Patchwerk
uv run tools/sim.py candidate/baseline.simc --fight DungeonSlice

# the loop (each iteration is one headless Claude Code turn following program.md)
./loop.sh 20
```

## Honesty section

- The stock Shadow APL is maintained by expert theorycrafters. Expect small gains on the stock
  profile and larger ones on a real character's gear, on odd fight profiles, and off-meta.
- Sims are models. A simmed gain that nobody can execute is not a gain. See playability rules.
- Everything in `results.tsv` is reproducible: same candidate hash, same seed, same simc commit.

## License

MIT. SimulationCraft is vendored separately under its own license.
