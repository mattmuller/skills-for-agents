# skills-for-agents

Agent skills that make a coding agent work the way a careful reviewer would. Each skill has an eval that compares it with no skill, and the numbers below include the ties.

| Skill | What it does | Test score: with skill vs without |
|---|---|---|
| [state-machine-audit](skills/state-machine-audit) | Finds hidden state machines (status columns, nullable timestamps, flags) and checks them for six bug shapes | 6 of 6 planted bugs vs 5 of 6 |
| [react-native-adaptive-layout](skills/react-native-adaptive-layout) | Makes a React Native or Expo app stop stretching on tablets and foldables | 16 of 16 vs about 9.5 of 16 |
| [cookieyes-gtm-assessment](skills/cookieyes-gtm-assessment) | Diagnoses a CookieYes banner loaded through Google Tag Manager with Consent Mode v2 | 14 of 14 vs 12.5 of 14 (small) |
| [skill-evals](skills/skill-evals) | Writes and runs skill evals with `claude plugin eval`, and avoids its traps | 15 of 15 vs 4 of 15 (least independent) |
| [gemini-reference-images](skills/gemini-reference-images) | Generates images from reference images with Gemini and debugs empty results | 17 of 17 vs about 9.5 of 17 |
| [css-scroll-driven-animations](skills/css-scroll-driven-animations) | Uses native CSS scroll-driven animations for parallax, reveals and progress bars | 15 of 15 vs 15 of 15 (no gain) |

We gave Claude the same tasks with and without each skill and marked the answers against a checklist. The score is checklist points earned. Full method, misses and limits are in `evals/<skill>/results.md`.

## Install

Add the marketplace once, then install what you want.

```
/plugin marketplace add mattmuller/skills-for-agents
/plugin install state-machine-audit@skills-for-agents
/plugin install react-native-adaptive-layout@skills-for-agents
/plugin install cookieyes-gtm-assessment@skills-for-agents
/plugin install skill-evals@skills-for-agents
/plugin install gemini-reference-images@skills-for-agents
/plugin install css-scroll-driven-animations@skills-for-agents
```

Or copy a folder from `skills/` into `~/.claude/skills/`. The folders follow the Agent Skills format, so other agents can read them.

## state-machine-audit

Finds every record whose behaviour depends on a status, a nullable timestamp or a flag, writes its states down, and checks six bug shapes. Also covers pin-then-refactor. On a small planted-bug app a plain agent found five of six shapes anyway; the skill's gain was the stuck state. One app, three runs per arm. Detail: `skills/state-machine-audit/README.md` and `evals/results.md`.

## react-native-adaptive-layout

One layout that stops stretching, not a tablet version: breakpoints from live width, a three-property content container, a table of what caps and what expands, and a rail-versus-bar pattern that avoids remounting on fold. Clear eval gain: baselines missed the container pattern, the orientation and native-tab traps, and tabletop posture. The device traps are the author's observations on one Expo SDK (dated in the skill); recheck them on yours.

## cookieyes-gtm-assessment

A step-by-step check for double banners, late consent defaults, a second consent source, Consent Mode v2 signals and CSP. Small eval gain: plain agents already find the usual causes. The skill adds a checklist and a habit of saying what was not checked. It carries no account IDs; you supply your own container.

## skill-evals

How to test whether a skill changes behaviour with `claude plugin eval`: read the delta, carry context in the prompt, include a control case, use pressure. It also lists four traps seen on CLI 2.1.278. The large gain is mostly those version-specific facts, which a model cannot guess. Recheck them on your CLI version.

## gemini-reference-images

Reference-image limits per Gemini model (dated 19 Sep 2026), the call shape, and six traps, notably that "no watermarks" can make the whole call refuse and that a refusal looks like an empty result. Clear eval gain. Both baselines advised the very wording the skill warns against. Nobody ran the API calls here.

## css-scroll-driven-animations

Native `animation-timeline` for scroll effects, with `overflow: hidden` freezing `view()`, the top-of-page range, and reduced-motion and fallback rules. No measured gain: Sonnet 5.5 already knew these on both test prompts. It may help weaker models; this eval does not show it.

## Limits of all evals

Two to three runs per arm on one model, graded by the skill's author. Prompts target what each skill covers. Treat the numbers as a rough check, not a benchmark.

MIT licence.
