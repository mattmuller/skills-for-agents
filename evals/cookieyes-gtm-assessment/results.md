# Results: cookieyes-gtm-assessment (9 Nov 2026)

| Prompt | Items | With skill (run 1, run 2) | Baseline (run 1, run 2) |
|---|---|---|---|
| ck-a: double banner and console error, snippets given | 7 | 7, 7 | 6, 6 |
| ck-b: analytics hit before consent, dataLayer log given | 7 | 7, 7 | 6, 7 |
| Total | 14 | 14, 14 | 12, 13 |

**Headline: small gain, 14 of 14 against 12.5 of 14.**

The baseline is already strong here. It found the duplicate load, the late trigger, the competing default-consent tag and the missing Consent Mode v2 signals. Its misses: both ck-a baselines called the GA4 setup-tag link on the consent tag fine or left it in place; one ck-b baseline did not name a duplicate loader as a possible cause (a close call, scored 0).

The with-skill answers were more careful in a different way that the rubric only partly rewards: they said what they could not check (no container export, no CSP headers) and told the reader to read the signal mapping from the dashboard. Baselines stated a few specifics (cookie names, `gcs` values) from memory.

This skill's main value is a checklist and honesty about scope, not hidden facts.

## Method

Model for every run: Sonnet 5.5 subagents, fresh context each. Two realistic prompts (`prompts/`). Two runs per arm per prompt. With-skill runs were told to read the skill's `SKILL.md` first. Baseline runs were told to answer from their own knowledge and not to use the Skill tool or read any skills folder. That isolation rests on the instruction only; I did not sandbox the filesystem.

The rubric (`rubric-*.md`) was written before the runs and kept out of the runs' reach. It is committed here after the runs. Each item scores 1 or 0. Run outputs are in `runs/`, verbatim apart from mechanical word swaps for neutrality (for example, a word describing image style) and local paths.

## Honest limits

- I wrote the skill, the prompts and the rubric, and I graded the answers. A grader agent or a second person would be more independent. Some rubric items were judgement calls; where one was close I note it below.
- Two runs per arm is a small sample. A one-point gap between runs is noise.
- The prompts target things the skill covers. That favours the skill. Read the per-item misses, not only the totals.
- Nobody ran the generated code or checked any answer on a device or browser. The scores measure whether an answer contains the checked points, not whether it works.
