#!/usr/bin/env python3
"""Append a result row to results.tsv.

usage: log.py <exp> <fight> <dps> <err> <apl_lines> <hash> <kept yes|no|tradeoff> "<hypothesis>"
Compares against the last kept row for the same fight (or baseline) and fills delta and z.
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TSV = ROOT / "results.tsv"
HEADER = "exp\tfight\tdps\terr\tdelta\tz\tapl_lines\thash\tkept\thypothesis\n"


def last_best(fight: str):
    if not TSV.exists():
        return None
    rows = [l.rstrip("\n").split("\t") for l in TSV.read_text().splitlines()[1:] if l.strip()]
    for r in reversed(rows):
        if r[1] == fight and r[8] in ("yes", "baseline"):
            return float(r[2]), float(r[3])
    return None


def main():
    exp, fight, dps, err, apl_lines, h, kept, hyp = sys.argv[1:9]
    dps, err = float(dps), float(err)
    best = last_best(fight)
    if best is None:
        delta, z = 0.0, 0.0
        if kept == "yes":
            kept = "baseline"
    else:
        delta = dps - best[0]
        z = delta / math.sqrt(err**2 + best[1]**2) if (err or best[1]) else 0.0
    if not TSV.exists():
        TSV.write_text(HEADER)
    with TSV.open("a") as f:
        f.write(f"{exp}\t{fight}\t{dps:.1f}\t{err:.1f}\t{delta:+.1f}\t{z:+.2f}\t{apl_lines}\t{h}\t{kept}\t{hyp}\n")
    print(f"{exp} {fight} {dps:.1f}±{err:.1f} delta={delta:+.1f} z={z:+.2f} kept={kept}")


if __name__ == "__main__":
    main()
