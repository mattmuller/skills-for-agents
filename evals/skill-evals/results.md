# Results: skill-evals (9 Nov 2026)

| Prompt | Items | With skill (run 1, run 2) | Baseline (run 1, run 2) |
|---|---|---|---|
| se-a: diagnose two 0.00 cases and one passing case | 8 | 8, 8 | 1, 1 |
| se-b: design a suite for a delete-confirmation skill | 7 | 7, 7 | 3, 3 |
| Total | 15 | 15, 15 | 4, 4 |

**Headline: large gain, 15 of 15 against 4 of 15.** This is the least independent result in the repo.

- se-a asks about `claude plugin eval` behaviour that a model cannot know without being told: the empty run directory, the ignored scaffold field, `--allow-tools`. The skill records those facts, so a gap is expected. Both baselines said plainly that they had not verified the CLI. They guessed wrong causes (script paths, permissions).
- se-b is the fairer test of the skill's advice on writing cases. Baselines wrote 7 or 8 cases with no pressure cases, relied on fixtures, and never said to read transcripts. With-skill answers wrote 4 cases with pressure, a control and self-contained prompts.
- The CLI traps were observed on one version (2.1.278). I did not re-run them on the current CLI (2.1.321 on my machine). Treat them as leads to check.

## Method

Model for every run: Sonnet 5.5 subagents, fresh context each. Two realistic prompts (`prompts/`). Two runs per arm per prompt. With-skill runs were told to read the skill's `SKILL.md` first. Baseline runs were told to answer from their own knowledge and not to use the Skill tool or read any skills folder. That isolation rests on the instruction only; I did not sandbox the filesystem.

The rubric (`rubric-*.md`) was written before the runs and kept out of the runs' reach. It is committed here after the runs. Each item scores 1 or 0. Run outputs are in `runs/`, verbatim apart from mechanical word swaps for neutrality (for example, a word describing image style) and local paths.

## Honest limits

- I wrote the skill, the prompts and the rubric, and I graded the answers. A grader agent or a second person would be more independent. Some rubric items were judgement calls; where one was close I note it below.
- Two runs per arm is a small sample. A one-point gap between runs is noise.
- The prompts target things the skill covers. That favours the skill. Read the per-item misses, not only the totals.
- Nobody ran the generated code or checked any answer on a device or browser. The scores measure whether an answer contains the checked points, not whether it works.
