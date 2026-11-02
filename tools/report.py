#!/usr/bin/env python3
"""Render results.tsv + notes.md into a markdown report (stdout).

usage: report.py [--out REPORT.md]
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()

    tsv = ROOT / "results.tsv"
    if not tsv.exists():
        sys.exit("no results.tsv yet")
    rows = [l.split("\t") for l in tsv.read_text().splitlines()[1:] if l.strip()]
    by_exp = defaultdict(dict)
    for r in rows:
        exp, fight, dps, err, delta, z, apl, h, kept, hyp = r
        by_exp[exp][fight] = dict(dps=float(dps), err=float(err), delta=float(delta), z=float(z), apl=int(apl), hash=h, kept=kept, hyp=hyp)

    base = by_exp.get("0", {})
    best = {}
    for exp in by_exp:
        for fight, v in by_exp[exp].items():
            if v["kept"] in ("yes", "baseline"):
                best[fight] = (exp, v)

    out = ["# autoresearch-wow report", ""]
    out.append(f"Experiments: {len(by_exp) - 1} · kept: {sum(1 for e in by_exp if e != '0' and any(v['kept'] == 'yes' for v in by_exp[e].values()))} · profiles: {', '.join(sorted(base))}")
    out.append("")
    out.append("## Current best vs stock")
    out.append("")
    out.append("| profile | stock DPS | best DPS | gain | from exp | APL lines |")
    out.append("|---|---|---|---|---|---|")
    for fight in sorted(base):
        b = base[fight]
        e, v = best.get(fight, ("0", b))
        gain = 100 * (v["dps"] - b["dps"]) / b["dps"]
        out.append(f"| {fight} | {b['dps']:,.0f} ± {b['err']:,.0f} | {v['dps']:,.0f} ± {v['err']:,.0f} | {gain:+.2f}% | {e} | {v['apl']} |")
    out.append("")
    out.append("## Every experiment")
    out.append("")
    out.append("| exp | hypothesis | " + " | ".join(f"{f} Δ (z)" for f in sorted(base)) + " | verdict |")
    out.append("|---|---|" + "---|" * len(base) + "---|")
    for exp in sorted(by_exp, key=lambda x: int(x) if x.isdigit() else 0):
        if exp == "0":
            continue
        cells = []
        verdict = "not kept"
        hyp = ""
        for fight in sorted(base):
            v = by_exp[exp].get(fight)
            if v:
                cells.append(f"{v['delta']:+,.0f} ({v['z']:+.1f})")
                hyp = v["hyp"]
                if v["kept"] == "yes":
                    verdict = "**kept**"
                elif v["kept"] == "tradeoff":
                    verdict = "tradeoff"
            else:
                cells.append("—")
        out.append(f"| {exp} | {hyp} | " + " | ".join(cells) + f" | {verdict} |")
    notes = ROOT / "notes.md"
    if notes.exists():
        out += ["", "## Lab notes", "", notes.read_text().split("\n", 4)[-1].strip()]
    text = "\n".join(out) + "\n"
    if a.out:
        a.out.write_text(text)
        print(f"wrote {a.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
