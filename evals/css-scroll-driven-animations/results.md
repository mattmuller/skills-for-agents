# Results: css-scroll-driven-animations (9 Nov 2026)

| Prompt | Items | With skill (run 1, run 2) | Baseline (run 1, run 2) |
|---|---|---|---|
| cs-a: stuck, barely moving hero parallax | 7 | 7, 7 | 7, 7 |
| cs-b: card reveal and progress bar in a server-rendered app | 8 | 8, 8 | 8, 8 |
| Total | 15 | 15, 15 | 15, 15 |

**Headline: no measured gain. A tie at 15 of 15.**

On these prompts a plain Sonnet 5.5 already knew the two traps (`overflow: hidden` freezing a `view()` timeline, and the top-of-page range), the reduced-motion rule and `@supports` fallbacks. Differences in style only: with-skill answers used the skill's `entry 100% exit 100%` fix; baselines used `scroll(root)` with a pixel range, which also works. With-skill answers cited a support date and said to recheck it.

The skill may still help a weaker model or an older one. This eval does not show it.

## Method

Model for every run: Sonnet 5.5 subagents, fresh context each. Two realistic prompts (`prompts/`). Two runs per arm per prompt. With-skill runs were told to read the skill's `SKILL.md` first. Baseline runs were told to answer from their own knowledge and not to use the Skill tool or read any skills folder. That isolation rests on the instruction only; I did not sandbox the filesystem.

The rubric (`rubric-*.md`) was written before the runs and kept out of the runs' reach. It is committed here after the runs. Each item scores 1 or 0. Run outputs are in `runs/`, verbatim apart from mechanical word swaps for neutrality (for example, a word describing image style) and local paths.

## Honest limits

- I wrote the skill, the prompts and the rubric, and I graded the answers. A grader agent or a second person would be more independent. Some rubric items were judgement calls; where one was close I note it below.
- Two runs per arm is a small sample. A one-point gap between runs is noise.
- The prompts target things the skill covers. That favours the skill. Read the per-item misses, not only the totals.
- Nobody ran the generated code or checked any answer on a device or browser. The scores measure whether an answer contains the checked points, not whether it works.
