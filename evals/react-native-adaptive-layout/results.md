# Results: react-native-adaptive-layout (9 Nov 2026)

| Prompt | Items | With skill (run 1, run 2) | Baseline (run 1, run 2) |
|---|---|---|---|
| rn-a: fix a phone-only screen for iPad and foldable | 8 | 8, 8 | 5, 6 |
| rn-b: plan a bottom bar to side rail switch | 8 | 8, 8 | 4, 4 |
| Total | 16 | 16, 16 | 9, 10 |

**Headline: clear gain, 16 of 16 against about 9.5 of 16.**

Where the baseline missed:
- rn-a: no `width: '100%'` plus `maxWidth` container pattern (both runs); both baselines changed the phone grid from 3 to 2 columns; neither said that media may expand while buttons and fields cap.
- rn-b: neither baseline named the iPad orientation trap (one stated it backwards: that the config "can be locked"); neither mentioned tabletop posture, that native tabs do not adapt on Android, or the iPad sidebar safe-area inset. Both baselines got the width-based rule, the one-navigator idea and the Android 16 orientation point right.

Caveat specific to this skill: the traps in `references/` come from the author's own emulator and simulator observations on one SDK. The with-skill answers repeated them, correctly or not. This eval cannot tell whether they still hold on a newer SDK.

## Method

Model for every run: Sonnet 5.5 subagents, fresh context each. Two realistic prompts (`prompts/`). Two runs per arm per prompt. With-skill runs were told to read the skill's `SKILL.md` first. Baseline runs were told to answer from their own knowledge and not to use the Skill tool or read any skills folder. That isolation rests on the instruction only; I did not sandbox the filesystem.

The rubric (`rubric-*.md`) was written before the runs and kept out of the runs' reach. It is committed here after the runs. Each item scores 1 or 0. Run outputs are in `runs/`, verbatim apart from mechanical word swaps for neutrality (for example, a word describing image style) and local paths.

## Honest limits

- I wrote the skill, the prompts and the rubric, and I graded the answers. A grader agent or a second person would be more independent. Some rubric items were judgement calls; where one was close I note it below.
- Two runs per arm is a small sample. A one-point gap between runs is noise.
- The prompts target things the skill covers. That favours the skill. Read the per-item misses, not only the totals.
- Nobody ran the generated code or checked any answer on a device or browser. The scores measure whether an answer contains the checked points, not whether it works.
