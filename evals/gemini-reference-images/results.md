# Results: gemini-reference-images (9 Nov 2026)

| Prompt | Items | With skill (run 1, run 2) | Baseline (run 1, run 2) |
|---|---|---|---|
| gm-a: intermittent empty image from a call with two references | 8 | 8, 8 | 3, 4 |
| gm-b: plan one image with 6 characters, 3 screens, 2 style references | 9 | 9, 9 | 6, 6 |
| Total | 17 | 17, 17 | 9, 10 |

**Headline: clear gain, 17 of 17 against 9.5 of 17.**

Where the baseline missed:
- gm-a: no baseline named the "no watermarks" wording as the trigger. Both asserted that `responseModalities` must be `['TEXT', 'IMAGE']`, which the skill's own observation contradicts (image-only worked in the author's tests). Neither moved the reference parts before the text.
- gm-b: both baselines recommended writing "no watermarks" in the prompt, the exact wording the skill says caused refusals. Neither knew the per-category limits (6 characters is over the limit of 4 or 5).
- Baselines were good on staging the build, compositing real screenshots afterwards and disclosure.

Not verified: the limits table and the watermark finding are the author's dated observations (Sep 2026). I did not call the API.

## Method

Model for every run: Sonnet 5.5 subagents, fresh context each. Two realistic prompts (`prompts/`). Two runs per arm per prompt. With-skill runs were told to read the skill's `SKILL.md` first. Baseline runs were told to answer from their own knowledge and not to use the Skill tool or read any skills folder. That isolation rests on the instruction only; I did not sandbox the filesystem.

The rubric (`rubric-*.md`) was written before the runs and kept out of the runs' reach. It is committed here after the runs. Each item scores 1 or 0. Run outputs are in `runs/`, verbatim apart from mechanical word swaps for neutrality (for example, a word describing image style) and local paths.

## Honest limits

- I wrote the skill, the prompts and the rubric, and I graded the answers. A grader agent or a second person would be more independent. Some rubric items were judgement calls; where one was close I note it below.
- Two runs per arm is a small sample. A one-point gap between runs is noise.
- The prompts target things the skill covers. That favours the skill. Read the per-item misses, not only the totals.
- Nobody ran the generated code or checked any answer on a device or browser. The scores measure whether an answer contains the checked points, not whether it works.
