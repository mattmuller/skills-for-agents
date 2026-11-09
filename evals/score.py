#!/usr/bin/env python3
"""Print per-shape detection from judgement files (one per run) against the answer key.

Usage: python3 evals/score.py judgement1.json [judgement2.json ...]
Each judgement: {"arm": "with_skill", "detected": ["missing-reverse", ...], "false_positives": 0}
"""
import json
import pathlib
import sys
from collections import defaultdict

key = json.loads((pathlib.Path(__file__).parent / "answer-key.json").read_text())
ids = [p["id"] for p in key["planted"]]
arms = defaultdict(list)
for path in sys.argv[1:]:
    j = json.loads(pathlib.Path(path).read_text())
    arms[j["arm"]].append(j)

for arm, runs in sorted(arms.items()):
    print(f"{arm}: {len(runs)} runs")
    for i in ids:
        hits = sum(i in r["detected"] for r in runs)
        print(f"  {i:24} {hits}/{len(runs)}")
    print(f"  {'false positives':24} {sum(r['false_positives'] for r in runs)} total")
