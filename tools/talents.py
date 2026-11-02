#!/usr/bin/env python3
"""Decode a talent loadout into readable rows.

usage: talents.py --track raid|dungeon
       talents.py "<talent string>"
       talents.py --file candidate/raid/talents.simc

simc's JSON never names talents, so this runs a 1-iteration sim with an HTML report and reads
the class / spec / hero talent tables out of it. Prints one line per tree row: taken nodes [rank].
"""
import argparse
import html
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIMC = Path(os.environ.get("SIMC", ROOT / "vendor/simc/build/simc"))


def decode(talent_lines: list[str]) -> str:
    base = (ROOT / "candidate/baseline.simc").read_text()
    with tempfile.TemporaryDirectory() as td:
        inp = Path(td) / "t.simc"
        out = Path(td) / "t.html"
        inp.write_text(base + "\n" + "\n".join(talent_lines) + "\n")
        subprocess.run([str(SIMC), str(inp), "iterations=1", "threads=1", f"html={out}"],
                       capture_output=True, text=True, check=False)
        if not out.exists():
            sys.exit("simc produced no html; is the talent string legal?")
        page = out.read_text(errors="ignore")
    lines = []
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>", page, re.S):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", m.group(1), re.S)]
        if len(cells) == 2 and re.search(r"Talents \[\d+\]$", cells[1]):
            lines.append(f"\n## {cells[1]}")
        elif len(cells) >= 8 and cells[0].isdigit() and any("[" in c for c in cells[1:]):
            taken = [c for c in cells[1:] if c]
            lines.append(f"row {cells[0]:>2}: " + " · ".join(taken))
    return "\n".join(lines).strip() or "no talent tables found in report"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("string", nargs="?")
    ap.add_argument("--track", choices=["raid", "dungeon"])
    ap.add_argument("--file", type=Path)
    a = ap.parse_args()
    if a.track:
        tl = (ROOT / "candidate" / a.track / "talents.simc").read_text().splitlines()
    elif a.file:
        tl = a.file.read_text().splitlines()
    elif a.string:
        tl = [f"talents={a.string}"]
    else:
        ap.error("give --track, --file or a talent string")
    tl = [l for l in tl if l.strip() and not l.startswith("#")]
    print(decode(tl))


if __name__ == "__main__":
    main()
