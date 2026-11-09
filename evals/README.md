# Evals

`sample-app/` is a small back office with eight state machines: six each carry one planted bug, two are clean decoys. `answer-key.json` says which is which. The key stays out of the copy an eval run reads.

Run one comparison arm:

1. Copy only the sample app: `cp -r evals/sample-app /tmp/run-app`
2. Start a fresh agent session with the prompt in `evals.json`. For the skill arm, tell it to read `skills/state-machine-audit/SKILL.md` first. For the baseline arm, say nothing about it.
3. Compare its `findings.md` with `answer-key.json` using `python3 evals/score.py findings-table.json`.

`score.py` reads a table of your judgements (`{"detected": ["missing-reverse", ...], "false_positives": 0}`) and prints per-shape hits. The judgement stays with a person or a grader agent: a finding counts only when it names the planted defect.
