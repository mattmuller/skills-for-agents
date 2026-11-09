# agent-skills

Agent skills that make a coding agent check its own work the way a careful reviewer would.

## state-machine-audit

Many records move through states that nobody wrote down: a `status` column, a nullable `deleted_at` or `expires_at`, a flag. Each function is correct alone, so tests pass. The bugs hide in the edges between states. This skill makes an agent find every such record, write down its states and transitions, and check each one against six bug shapes.

It also covers the safe way to refactor this logic: pin every transition with a test first, then change the code.

### Install

```
/plugin marketplace add mattmuller/agent-skills
/plugin install state-machine-audit@agent-skills
```

Or copy `skills/state-machine-audit` into `~/.claude/skills/`. It follows the Agent Skills format, so other agents can read the same folder.

### Use it

Ask in plain words:

```
Audit this repo for state machines and the bugs in them.
```

### What you get

The agent writes each machine down, then lists findings with where, who can reach it, and how serious. A short example from the sample app in this repo:

```
Machine: loans.status
  open -> overdue      nightly job
  open/overdue -> closed   staff, when the book is returned
  rule: closing a loan stops all notices

Finding [Important] gate missing on one path
  notifier.py:9  the nightly job selects by due date only.
  Reach: every loan returned late. Up to three false notices each.
  Fix: add status = 'overdue' to the query.
```

### The six bug shapes

1. A forward move with no way back.
2. A reverse move that forgets a side effect (restore leaves attachments archived).
3. A state nothing can leave.
4. An expiry that is stored but never checked.
5. One code path that skips a check the others make.
6. A status column that accepts any text.

### Does it work?

`evals/sample-app` is a small back office with each shape planted once and two clean state machines as decoys. The answer key is kept apart from what the agent reads. Three runs per arm, Sonnet 5.5, graded by hand. Numbers are bugs found out of 3 runs.

| Planted bug | With skill | No skill |
|---|---|---|
| Missing reverse | 3 | 3 |
| Side effect not undone | 3 | 3 |
| Stuck state | 3 | 1 |
| Expiry never checked | 3 | 3 |
| Gate missing on one path | 3 | 3 |
| No database guard | 3 | 3 |

On this small app, a plain agent already finds five of six shapes every time. The skill's clear gain is the stuck state, which needs a check that the way out is reachable. Both arms also reported real minor gaps in the decoys. No run called a state that is final by design a bug. Details, and why the stuck-state row is the weakest evidence, are in `evals/results.md`.

### Limits

- Three runs per arm is a small sample, on one app, in Python and SQL.
- The planted bugs and the skill have the same author.
- The pin-then-refactor step was not evaluated.
- The skill reads code. It does not run your app or see jobs and handlers outside the folders it reads.

### Layout

```
skills/state-machine-audit/   SKILL.md and references/
evals/                        sample app, answer key, run outputs, results
.claude-plugin/               marketplace.json
```

MIT licence.
