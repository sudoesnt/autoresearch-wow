#!/usr/bin/env bash
# Run N autoresearch turns. Each turn is one headless Claude Code session following program.md.
# usage: ./loop.sh [turns=10] [model=]
set -euo pipefail
cd "$(dirname "$0")"
turns="${1:-10}"
for ((i=1; i<=turns; i++)); do
  n=$(($(grep -c . results.tsv 2>/dev/null || echo 1)))
  echo "=== turn $i (results rows so far: $n) $(date +%H:%M:%S)"
  env -u CLAUDECODE claude -p \
    "Read program.md, then the tail of results.tsv and notes.md. Run exactly one experiment turn as program.md describes, then stop." \
    --permission-mode acceptEdits \
    --allowedTools "Bash(uv run tools/*),Bash(git *),Read,Edit,Write" \
    --max-turns 40 \
    --output-format text ${2:+--model "$2"} | tail -20
done
