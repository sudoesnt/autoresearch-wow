#!/usr/bin/env python3
"""Run SimulationCraft on a candidate and print one line of results.

usage: sim.py --track raid|dungeon [--fight raid|dungeon] [--target-error 0.2] [--json]
       sim.py <file.simc> --fight raid|dungeon

A track is candidate/<track>/{talents,apl}.simc on top of the shared candidate/baseline.simc.
--fight defaults to the track's own profile; pass it explicitly to cross-check a track on the
other profile.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIMC = Path(os.environ.get("SIMC", ROOT / "vendor/simc/build/simc"))
RUNS = ROOT / "runs"

FIGHTS = {
    "raid": ["fight_style=Patchwerk", "max_time=300", "desired_targets=1"],
    "dungeon": ["fight_style=DungeonSlice"],
}


def assemble(track_dir: Path | None, file: Path | None) -> tuple[str, int]:
    if file is not None:
        return file.read_text(), 0
    parts = []
    for p in (ROOT / "candidate/baseline.simc", track_dir / "talents.simc", track_dir / "apl.simc"):
        if p.exists():
            parts.append(f"# ---- {p.relative_to(ROOT)}\n" + p.read_text())
    apl = track_dir / "apl.simc"
    apl_lines = sum(1 for l in apl.read_text().splitlines() if l.strip() and not l.lstrip().startswith("#")) if apl.exists() else 0
    return "\n".join(parts), apl_lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", type=Path, help="a complete .simc file instead of a track")
    ap.add_argument("--track", choices=FIGHTS, help="candidate/<track>/ to sim")
    ap.add_argument("--fight", choices=FIGHTS, help="profile to score on (default: the track's own)")
    ap.add_argument("--target-error", type=float, default=0.2)
    ap.add_argument("--threads", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--json", action="store_true", help="print the full result record as JSON")
    a = ap.parse_args()

    if not SIMC.exists():
        sys.exit(f"simc binary not found at {SIMC}; build it or set SIMC=")

    if a.track is None and a.file is None:
        ap.error("give --track or a .simc file")
    fight = a.fight or a.track
    if fight is None:
        ap.error("--fight is required with a file")
    track_dir = ROOT / "candidate" / a.track if a.track else None
    text, apl_lines = assemble(track_dir, a.file)
    digest = hashlib.sha256(text.encode()).hexdigest()[:10]
    RUNS.mkdir(exist_ok=True)
    run_id = f"{time.strftime('%Y%m%d-%H%M%S')}-{a.track or 'file'}-on-{fight}-{digest}"
    inp = RUNS / f"{run_id}.simc"
    out = RUNS / f"{run_id}.json"
    inp.write_text(text)

    cmd = [str(SIMC), str(inp), *FIGHTS[fight],
           f"target_error={a.target_error}", f"threads={a.threads}",
           "report_details=0", "optimal_raid=1", f"json2={out}"]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    secs = time.time() - t0
    if proc.returncode != 0 or not out.exists():
        err = (proc.stderr or proc.stdout).strip().splitlines()
        msg = err[-1] if err else "unknown simc failure"
        rec = {"run": run_id, "track": a.track, "fight": fight, "hash": digest, "ok": False, "error": msg, "secs": round(secs, 1)}
        print(json.dumps(rec) if a.json else f"FAIL {a.track or a.file} on {fight} {digest} :: {msg}")
        return 1

    data = json.loads(out.read_text())
    player = data["sim"]["players"][0]
    cd = player["collected_data"]
    dps, err = cd["dps"]["mean"], cd["dps"]["mean_std_dev"]
    iters = (data["sim"]["options"].get("iterations")
             or cd["dps"].get("count")
             or data["sim"]["statistics"].get("total_iterations", 0))
    rec = {
        "run": run_id, "track": a.track, "fight": fight, "hash": digest, "ok": True,
        "dps": round(dps, 1), "err": round(err, 1), "err_pct": round(100 * err / dps, 3),
        "iterations": iters, "apl_lines": apl_lines, "secs": round(secs, 1),
        "talents": player.get("talents", ""), "simc_version": data["version"],
    }
    if a.json:
        print(json.dumps(rec))
    else:
        label = f"{a.track or 'file'}→{fight}"
        print(f"{label:16s} {dps:10.1f} ± {err:6.1f}  ({rec['err_pct']}%)  iters={iters}  apl_lines={apl_lines}  {secs:5.1f}s  {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
